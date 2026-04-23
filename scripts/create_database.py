# scripts/create_database.py
from sqlalchemy import create_engine

from tables import Base


def main() -> None:
    # This is the connection string for your Docker DB
    # format: postgresql://user:password@host:port/dbname
    db_url = "postgresql://devdocker:devpassword@localhost:5432/qffun"

    engine = create_engine(db_url, echo=True)  # echo=True prints the SQL commands in your terminal

    print("Creating tables...")
    Base.metadata.create_all(engine)
    print("Done!")


if __name__ == "__main__":
    main()
