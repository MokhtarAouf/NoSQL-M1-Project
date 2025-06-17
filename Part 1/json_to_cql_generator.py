import json

def get_nested(d, *keys):
    for key in keys:
        if d is None:
            return None
        d = d.get(key)
    return d

def escape(text):
    return text.replace("'", "''") if isinstance(text, str) else text

def cassandra_value(val):
    """Convert Python value to a safe CQL literal."""
    if val is None:
        return "null"
    if isinstance(val, str):
        return f"'{escape(val)}'"
    return val

def clean_decimal(val):
    """Ensure the value is a valid CQL decimal or return null."""
    if val is None:
        return "null"
    if isinstance(val, (int, float)):
        return val
    if isinstance(val, str):
        try:
            cleaned = val.replace('$', '').replace(',', '').strip()
            return float(cleaned)
        except:
            return "null"
    return "null"

insert_statements = []

with open("cleaned-companies2.json", "r") as file:
    for line in file:
        if not line.strip():
            continue  # skip empty lines
        company = json.loads(line)

        insert = f"""
        INSERT INTO companies (
            permalink, name, category_code, description, homepage_url,
            founded_year, founded_month, founded_day,
            deadpooled_year, deadpooled_month, deadpooled_day,
            number_of_employees, email_address, phone_number,
            total_money_raised, overview, twitter_username,
            acquisition_price_amount, acquisition_acquired_year,
            acquisition_acquired_month, acquisition_acquired_day,
            acquisition_acquiring_company
        ) VALUES (
            {cassandra_value(company.get("permalink"))},
            {cassandra_value(company.get("name"))},
            {cassandra_value(company.get("category_code"))},
            {cassandra_value(company.get("description"))},
            {cassandra_value(company.get("homepage_url"))},
            {cassandra_value(company.get("founded_year"))},
            {cassandra_value(company.get("founded_month"))},
            {cassandra_value(company.get("founded_day"))},
            {cassandra_value(company.get("deadpooled_year"))},
            {cassandra_value(company.get("deadpooled_month"))},
            {cassandra_value(company.get("deadpooled_day"))},
            {cassandra_value(company.get("number_of_employees"))},
            {cassandra_value(company.get("email_address"))},
            {cassandra_value(company.get("phone_number"))},
            {cassandra_value(company.get("total_money_raised"))},
            {cassandra_value(company.get("overview"))},
            {cassandra_value(company.get("twitter_username"))},
            {clean_decimal((company.get("acquisition") or {}).get("price_amount"))},
            {cassandra_value((company.get("acquisition") or {}).get("acquired_year"))},
            {cassandra_value((company.get("acquisition") or {}).get("acquired_month"))},
            {cassandra_value((company.get("acquisition") or {}).get("acquired_day"))},
            {cassandra_value(get_nested(company.get("acquisition"), "acquiring_company", "name"))}
        );
        """.strip()

        insert_statements.append(insert)

schema_header = """
CREATE KEYSPACE IF NOT EXISTS PROJECT WITH REPLICATION = {'class': 'SimpleStrategy', 'replication_factor': 1};
USE PROJECT;

CREATE TABLE IF NOT EXISTS companies (
    permalink text PRIMARY KEY,
    name text,
    category_code text,
    description text,
    homepage_url text,
    founded_year int,
    founded_month int,
    founded_day int,
    deadpooled_year int,
    deadpooled_month int,
    deadpooled_day int,
    number_of_employees int,
    email_address text,
    phone_number text,
    total_money_raised text,
    overview text,
    twitter_username text,
    acquisition_price_amount decimal,
    acquisition_acquired_year int,
    acquisition_acquired_month int,
    acquisition_acquired_day int,
    acquisition_acquiring_company text
);
""".strip()

with open("insert_companies.cql", "w") as out_file:
    out_file.write(schema_header + "\n\n")
    out_file.write("\n\n".join(insert_statements))

print("✅ Script insert_companies.cql généré avec succès.")
