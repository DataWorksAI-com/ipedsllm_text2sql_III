# Author: Liran
# Description: This file contains the TableFormatter class, which is responsible for formatting the table context retrived after semantic search into a string

from typing import List, Any

class TableFormatter:

    #function to  Formats the provided table context into a  string
    def docs2str(self, tables_context:List[Any]) -> str:
        str_context = ""
        for ix, table_info in enumerate(tables_context):
            table_name = table_info.get("Table_Name")
            # table_description = table_info.get("Table_Description")
            column_name = table_info.get("Column_Names")
            # column_description = table_info.get("Column_Description")
            
            # Format the information about the table, including its index, description, columns, and sample rows
            str_context += f"{ix + 1}. Table: {table_name}\n"
            # str_context += f"   Description: {table_description}\n"
            str_context += f"   Column Name: {column_name}\n"
            # str_context += f"   Column Description: {column_description}\n"
        return str_context
