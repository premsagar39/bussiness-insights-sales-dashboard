"""Prepare Superstore data, execute MySQL SQL and refresh the Power BI source."""
from pathlib import Path
import argparse,base64,gzip,hashlib,json,os,re,getpass
from datetime import datetime,timezone
import pandas as pd
import pymysql

MARKER="superstore_python_mysql_powerbi_v1"
Q=chr(96)
def statements(path):
    return [q.strip() for q in path.read_text(encoding="utf8").split(";") if q.strip()]
def named_queries(path):
    for chunk in re.split(r"-- name:\s*",path.read_text(encoding="utf8"))[1:]:
        name,query=chunk.split("\n",1)
        yield name.strip(),query.strip().rstrip(";").strip()
def query_frame(con,query):
    with con.cursor() as cur:
        cur.execute(query)
        return pd.DataFrame(cur.fetchall(),columns=[x[0] for x in cur.description])

def run(source,project,host,port,user,database,password):
    project=Path(project).resolve();source=Path(source).resolve()
    model_root=project if (project/"Superstore_Sales_Insights.SemanticModel/model.bim").is_file() else project/"powerbi-source"
    if not (model_root/"Superstore_Sales_Insights.SemanticModel/model.bim").is_file():
        raise FileNotFoundError("Extract powerbi-source.zip into powerbi-source first.")
    if not re.fullmatch(r"[A-Za-z0-9_]+",database):raise ValueError("Invalid database name.")
    raw=pd.read_csv(source,encoding="cp1252")
    required={"RowID","OrderID","Sales","Profit","OrderDate","ShipDate","CustomerID","ProductName","ProductCategory","ProductSubCategory"}
    if not required.issubset(raw.columns):raise ValueError("Use the compact-column Superstore CSV.")
    if raw.duplicated().any():raise ValueError("Review exact duplicate rows before loading.")
    df=raw.copy()
    for col in df.select_dtypes(include=["object","str"]):df[col]=df[col].str.strip()
    for col in ["OrderDate","ShipDate"]:df[col]=pd.to_datetime(df[col],errors="raise")
    if df[["OrderDate","ShipDate","Sales","Profit","OrderID","CustomerID"]].isna().any().any():
        raise ValueError("Required analysis fields contain missing values.")
    if (df.ShipDate<df.OrderDate).any():raise ValueError("Ship dates precede order dates.")
    df.insert(0,"LineKey",range(1,len(df)+1))
    for col in ["OrderDate","ShipDate"]:df[col]=df[col].dt.strftime("%Y-%m-%d")
    password=password if password is not None else getpass.getpass("MySQL password: ")
    options=dict(host=host,port=port,user=user,password=password,charset="utf8mb4",connect_timeout=10)
    queries=project/"queries";reports=project/"reports";(reports/"sql_results").mkdir(parents=True,exist_ok=True)
    with pymysql.connect(**options,autocommit=True) as con:
        with con.cursor() as cur:
            cur.execute("SELECT SCHEMA_NAME FROM INFORMATION_SCHEMA.SCHEMATA WHERE SCHEMA_NAME=%s",(database,))
            existed=cur.fetchone() is not None
            if existed:
                cur.execute("SELECT TABLE_NAME FROM INFORMATION_SCHEMA.TABLES WHERE TABLE_SCHEMA=%s AND TABLE_NAME='pipeline_metadata'",(database,))
                if cur.fetchone() is None:raise ValueError("Existing schema is not owned by this pipeline. Choose a new database.")
                cur.execute(f"SELECT marker FROM {Q}{database}{Q}.pipeline_metadata")
                if cur.fetchone()!=(MARKER,):raise ValueError("Unrecognized schema marker. Choose a new database.")
            else:cur.execute(f"CREATE DATABASE {Q}{database}{Q} CHARACTER SET utf8mb4 COLLATE utf8mb4_bin")
            cur.execute(f"USE {Q}{database}{Q}");cur.execute("SET lc_time_names='en_US'")
            cur.execute("SELECT VERSION()");version=cur.fetchone()[0]
            if not existed:
                cur.execute("CREATE TABLE pipeline_metadata(marker VARCHAR(80) NOT NULL)")
                cur.execute("INSERT INTO pipeline_metadata VALUES(%s)",(MARKER,))
                for q in statements(queries/"00_schema.sql"):cur.execute(q)
            for view in ["vw_powerbi_sales","vw_powerbi_products","vw_powerbi_dates"]:cur.execute(f"DROP VIEW IF EXISTS {Q}{view}{Q}")
            for table in ["fact_sales","dim_products","dim_dates","stg_sales"]:cur.execute(f"DELETE FROM {Q}{table}{Q}")
            clean=df.astype(object).where(pd.notna(df),None)
            rows=[tuple(v.item() if hasattr(v,"item") else v for v in row) for row in clean.itertuples(index=False,name=None)]
            columns=",".join(Q+c+Q for c in clean.columns)
            cur.executemany(f"INSERT INTO stg_sales({columns}) VALUES({','.join(['%s']*len(clean.columns))})",rows)
            for q in statements(queries/"00_reporting_views.sql"):cur.execute(q)
        frames={name:query_frame(con,q) for name,q in named_queries(queries/"Power bi used queries")}
        results={}
        for path in sorted(queries.glob("0[1-9]_*.sql")):
            for name,q in named_queries(path):
                result=query_frame(con,q);result.to_csv(reports/"sql_results"/(name+".csv"),index=False)
                results[name]={"rows":len(result),"sql_file":"queries/"+path.name}
        q=next(q for name,q in named_queries(queries/"01_basic_queries.sql") if name=="portfolio_kpis")
        k=query_frame(con,q).iloc[0];sql_sales=float(k.Sales);sql_profit=float(k.Profit)
        checks={
            "order_lines":int(k.OrderLines)==len(raw),
            "distinct_orders":int(k.Orders)==int(raw.OrderID.nunique()),
            "distinct_customers":int(k.Customers)==int(raw.CustomerID.nunique()),
            "sales":abs(sql_sales-float(raw.Sales.sum()))<0.00001,
            "profit":abs(sql_profit-float(raw.Profit.sum()))<0.00001,
            "missing_base_margin_preserved":int(frames["sales"].ProductBaseMargin.isna().sum())==int(raw.ProductBaseMargin.isna().sum()),
            "no_join_fanout":len(frames["sales"])==len(raw),
            "product_key_coverage":bool(frames["sales"].ProductKey.isin(frames["products"].ProductKey).all())}
        expected_days=(pd.to_datetime(frames["sales"].ShipDate)-pd.to_datetime(frames["sales"].OrderDate)).dt.days
        checks["sql_shipping_days"]=expected_days.equals(frames["sales"]["Days to Ship"].astype("int64"))
        expected_band=frames["sales"].Discount.astype(float).map(lambda x:"No discount" if x==0 else "01–05%" if x<=.05 else "06–10%" if x<=.10 else "Above 10%")
        checks["sql_discount_bands"]=expected_band.equals(frames["sales"]["Discount Band"])
        monthly=pd.read_csv(reports/"sql_results/cumulative_monthly_sales.csv")
        checks["sql_running_total"]=abs(float(monthly.CumulativeSales.iloc[-1])-sql_sales)<0.00001
        joined=pd.read_csv(reports/"sql_results/join_reconciliation.csv").iloc[0]
        checks["sql_join_reconciliation"]=int(joined.SourceLines)==int(joined.JoinedLines)==len(raw)
        if not all(checks.values()):raise AssertionError({a:b for a,b in checks.items() if not b})
    data=project/"data";data.mkdir(exist_ok=True)
    for name,frame in frames.items():
        frame.to_csv(data/(name+".csv"),index=False)
        if model_root!=project:
            (model_root/"data").mkdir(exist_ok=True)
            frame.to_csv(model_root/"data"/(name+".csv"),index=False)
    model_path=model_root/"Superstore_Sales_Insights.SemanticModel/model.bim"
    model=json.loads(model_path.read_text(encoding="utf-8-sig"))
    sales_table=next(t for t in model["model"]["tables"] if t["name"]=="Sales")
    for col in sales_table["columns"]:
        if col["name"] in ["Days to Ship","Discount Band"]:
            col.pop("expression",None);col.pop("type",None);col["sourceColumn"]=col["name"]
    types={"dateTime":"type date","int64":"Int64.Type","double":"type number","string":"type text"}
    for table in model["model"]["tables"]:
        name=table["name"].lower()
        if name not in frames:continue
        packed=base64.b64encode(gzip.compress(frames[name].to_csv(index=False).encode("utf8"),mtime=0)).decode()
        pairs=", ".join('{"'+c["sourceColumn"]+'",'+types[c["dataType"]]+'}' for c in table["columns"] if "sourceColumn" in c)
        expression='let\n // SQL output from MySQL view vw_powerbi_'+name+'. Rebuild using src/run_pipeline.py.\n Source=Csv.Document(Binary.Decompress(Binary.FromText("'+packed+'",BinaryEncoding.Base64),Compression.GZip),[Delimiter=",",Encoding=65001,QuoteStyle=QuoteStyle.Csv]),\n Headers=Table.PromoteHeaders(Source,[PromoteAllScalars=true]),\n Typed=Table.TransformColumnTypes(Headers,{'+pairs+'},"en-US")\nin Typed'
        table["partitions"][0]["source"]["expression"]=expression.splitlines()
    annotations=model["model"].setdefault("annotations",[])
    annotations[:]=[a for a in annotations if a["name"]!="SourceWorkflow"]
    annotations.append({"name":"SourceWorkflow","value":"Python preparation -> MySQL 8 staging, joins, SQL calculations and views -> embedded SQL exports -> Power BI/DAX"})
    model_path.write_text(json.dumps(model,ensure_ascii=False,indent=2)+"\n",encoding="utf8")
    runlog={"workflow":"Python -> MySQL 8 -> Power BI","mysql_version":version,
        "source_file":source.name,"source_sha256":hashlib.sha256(source.read_bytes()).hexdigest(),
        "executed_at_utc":datetime.now(timezone.utc).isoformat(),"source_rows":len(raw),
        "source_distinct_row_ids":int(raw.RowID.nunique()),"sales":sql_sales,"profit":sql_profit,
        "orders":int(k.Orders),"customers":int(k.Customers),"analysis_queries_executed":len(results),
        "powerbi_sql_exports":{name:len(f) for name,f in frames.items()},"checks":checks,
        "query_files_sha256":{p.name:hashlib.sha256(p.read_bytes()).hexdigest() for p in queries.iterdir() if p.is_file()},
        "analysis_results":results}
    (reports/"pipeline_run.json").write_text(json.dumps(runlog,indent=2)+"\n",encoding="utf8")
    print(f"MySQL {version}: {len(raw):,} rows; {len(results)} analysis queries; all {len(checks)} reconciliation checks passed.")
    print("Updated SQL exports and Power BI source. Open the PBIP, Refresh, then Save as PBIX.")
    return runlog

def main():
    project=Path(__file__).resolve().parents[1]
    parser=argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--source",type=Path,default=project/"dataset/SuperStoreUS-2015 new .csv")
    parser.add_argument("--project",type=Path,default=project)
    parser.add_argument("--mysql-host",default=os.getenv("MYSQL_HOST","127.0.0.1"))
    parser.add_argument("--mysql-port",type=int,default=int(os.getenv("MYSQL_PORT","3306")))
    parser.add_argument("--mysql-user",default=os.getenv("MYSQL_USER","root"))
    parser.add_argument("--database",default=os.getenv("MYSQL_DATABASE","business_insights_sales"))
    a=parser.parse_args()
    run(a.source,a.project,a.mysql_host,a.mysql_port,a.mysql_user,a.database,os.getenv("MYSQL_PASSWORD"))
if __name__=="__main__":main()
