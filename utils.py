import os
import httpx
import pandas as pd
import io
from zipfile import ZipFile
from fastapi import HTTPException
from dotenv import load_dotenv
from sqlalchemy import select

from typing import List

from models import Employee, Team

load_dotenv()

api_username = os.getenv("api_username")
api_password = os.getenv("api_password")
api_url = os.getenv("api_url")
api_endpoint = os.getenv("api_endpoint")

app_username = os.getenv("app_username")
app_password = os.getenv("app_password")


def get_connection():
    connection = httpx.Client(auth=(api_username, api_password))
    return connection


def get_df():
    try:
        client = get_connection()
        response = client.get(f"{api_url}{api_endpoint}")
        response.raise_for_status()
        tokens_zip_content = response.content

        with io.BytesIO(tokens_zip_content) as zip_buffer:
            with ZipFile(zip_buffer, "r") as zip_file:
                xlsx_file = [name for name in zip_file.namelist() if name.endswith(".xlsx")]

                if not xlsx_file:
                    raise HTTPException(status_code=400, detail="No .xlsx file found in the archive")

                with zip_file.open(xlsx_file[0]) as excel_file:
                    df = pd.read_excel(excel_file, engine="openpyxl")
        return df
    except httpx.HTTPError as e:
        raise HTTPException(status_code=e.response.status_code, detail="External API error")


async def get_api_data(id: int = None):
    # try:
    df = get_df()

    if id is not None:
        # log id
        df = df[df['ID'] == int(id)]

    processed_data = []
    for token in df["Token"]:
        try:
            async with httpx.AsyncClient() as client:
                response = await client.get(
                    f"{api_url}{api_endpoint}/{token}",
                    auth=(api_username, api_password)
                )
                response.raise_for_status()
                processed_data.append(response.json())

        except httpx.HTTPError as err:
            processed_data.append({"id": token, "error": str(err)})
    return processed_data


def get_db_data(db, id: int = None):

    query = (
        select(
            Employee.id,
            Employee.email,
            Employee.reports,
            Employee.position,
            Employee.hired,
            Employee.salary,
            Team.team_name.label("team")
        )
        .outerjoin(Team)
    )

    if id is not None:
        result = db.execute(query.filter(Employee.id == id)).fetchall()
    else:
        result = db.execute(query).fetchall()
    return [row._mapping for row in result]


def combine_data(df_api_data: List, df_db_data: List):
    df_api = pd.DataFrame(df_api_data)
    df_db = pd.DataFrame(df_db_data)

    joined_df = pd.merge(df_api, df_db, on='id', how='outer')
    joined_df['email'] = joined_df['email_x'].fillna(joined_df['email_y'])
    joined_df.drop(['email_x', 'email_y'], axis=1, inplace=True)
    joined_df['reports'] = pd.to_numeric(joined_df['reports'], errors='coerce').astype('Int64')
    desired_order = ['id', 'email', 'phone', 'full_name', 'first_name', 'last_name', 'gender', 'birth', 'reports',
                     'position', 'hired', 'salary', 'team']
    joined_df = joined_df[desired_order]

    return joined_df.to_dict(orient='records')
