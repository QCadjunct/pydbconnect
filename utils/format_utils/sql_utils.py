# pydatabaseconnection/utils/format_utils/sql_utils.py
from typing import Dict, Any, Optional, List, Tuple
import re
from pathlib import Path
import sqlparse
from collections import defaultdict

class SQLUtils:
    """Utilities for SQL format operations"""
    
    @staticmethod
    def parse_sql_file(
        path: Path,
        strip_comments: bool = True
    ) -> List[str]:
        """Parse SQL file into individual statements"""
        with open(path, 'r') as f:
            content = f.read()
            
        # Format SQL
        formatted = sqlparse.format(
            content,
            strip_comments=strip_comments,
            reindent=True
        )
        
        # Split into statements
        return [
            stmt.strip() for stmt in sqlparse.split(formatted)
            if stmt.strip()
        ]

    @staticmethod
    def analyze_schema(sql: str) -> Dict[str, Any]:
        """Analyze CREATE TABLE schema"""
        parsed = sqlparse.parse(sql)[0]
        analysis = {
            "table_name": "",
            "columns": [],
            "primary_key": None,
            "foreign_keys": [],
            "indexes": [],
            "constraints": []
        }
        
        def extract_table_name(token):
            if token.get_name():
                analysis["table_name"] = token.get_name()

        def extract_columns(token):
            if isinstance(token, sqlparse.sql.Parenthesis):
                for item in token.tokens:
                    if isinstance(item, sqlparse.sql.IdentifierList):
                        for identifier in item.get_identifiers():
                            col_def = str(identifier).strip()
                            analysis["columns"].append(col_def)
                            
                            # Check for primary key in column definition
                            if "PRIMARY KEY" in col_def.upper():
                                analysis["primary_key"] = col_def.split()[0]

        # Process tokens
        for token in parsed.tokens:
            if token.is_group:
                extract_table_name(token)
                extract_columns(token)
            
        return analysis

    @staticmethod
    def generate_batch_inserts(
        table_name: str,
        columns: List[str],
        batch_size: int = 1000
    ) -> str:
        """Generate batched INSERT statements"""
        placeholders = ', '.join(['?'] * len(columns))
        batch_placeholders = ', '.join([f'({placeholders})'] * batch_size)
        
        return f"""
        INSERT INTO {table_name} 
        ({', '.join(columns)})
        VALUES {batch_placeholders}
        """

    @staticmethod
    def extract_dependencies(
        sql: str
    ) -> Dict[str, List[str]]:
        """Extract table dependencies from SQL"""
        dependencies = defaultdict(list)
        
        # Find table references
        tables = re.findall(
            r'(?i)(?:FROM|JOIN|UPDATE|INTO)\s+([a-zA-Z_][a-zA-Z0-9_]*)',
            sql
        )
        
        # Find foreign key relationships
        fk_pattern = r'(?i)FOREIGN\s+KEY.*REFERENCES\s+([a-zA-Z_][a-zA-Z0-9_]*)'
        foreign_keys = re.findall(fk_pattern, sql)
        
        for table in tables:
            for fk in foreign_keys:
                if fk != table:
                    dependencies[table].append(fk)
                    
        return dict(dependencies)

    @staticmethod
    def optimize_indexes(
        sql: str,
        table_stats: Optional[Dict[str, Any]] = None
    ) -> List[str]:
        """Generate optimized index statements"""
        analysis = SQLUtils.analyze_schema(sql)
        indexes = []
        
        if table_stats:
            # Suggest indexes based on table statistics
            for col, stats in table_stats.items():
                if stats.get('unique_ratio', 0) > 0.8:
                    indexes.append(f"CREATE UNIQUE INDEX idx_{col} ON {analysis['table_name']}({col});")
                elif stats.get('null_ratio', 0) < 0.2:
                    indexes.append(f"CREATE INDEX idx_{col} ON {analysis['table_name']}({col});")
                    
        return indexes
