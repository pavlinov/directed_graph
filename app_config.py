assets_path = './assets'
xmls_path = './xmls'
xml_schema = f'{xmls_path}/directed_graph_schema.xsd'
xml_document = f'{xmls_path}/directed_graph.xml'
png_image = f'{assets_path}/graph_with_cycles.png'

db_connection = dict(
    dbname="postgres",
    user="postgres",
    password="example",
    host="localhost",
    port="5432"
)

dsn = f'postgresql://{db_connection["user"]}:{db_connection["password"]}@{db_connection["host"]}:{db_connection["port"]}/{db_connection["dbname"]}'
