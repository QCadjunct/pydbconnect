# pydatabaseconnection/utils/format_utils/avro_utils.py
import fastavro
import json
from typing import Dict, Any, Optional, List
from pathlib import Path

class AvroUtils:
    """Utilities for Apache Avro operations"""
    
    @staticmethod
    def infer_schema(
        data: Dict[str, Any],
        nullable: bool = True
    ) -> Dict[str, Any]:
        """Infer Avro schema from data"""
        type_mapping = {
            int: "long",
            float: "double",
            str: "string",
            bool: "boolean",
            bytes: "bytes",
            list: "array",
            dict: "map",
            type(None): "null"
        }
        
        def _infer_type(value: Any) -> Dict[str, Any]:
            if value is None:
                return {"type": "null"}
                
            value_type = type(value)
            if value_type in type_mapping:
                avro_type = type_mapping[value_type]
                return {"type": [avro_type, "null"]} if nullable else {"type": avro_type}
                
            if isinstance(value, list):
                if not value:
                    return {"type": "array", "items": "string"}  # Default to string
                return {
                    "type": "array",
                    "items": _infer_type(value[0])
                }
                
            if isinstance(value, dict):
                return {
                    "type": "record",
                    "name": "AnonymousRecord",
                    "fields": [
                        {"name": k, "type": _infer_type(v)}
                        for k, v in value.items()
                    ]
                }
                
            return {"type": "string"}  # Default fallback
        
        schema = _infer_type(data)
        schema["name"] = "AutoSchema"
        return schema

    @staticmethod
    def optimize_schema(
        schema: Dict[str, Any],
        data_sample: Optional[List[Dict[str, Any]]] = None
    ) -> Dict[str, Any]:
        """Optimize Avro schema based on data patterns"""
        def _optimize_field(field: Dict[str, Any], sample_data: List[Any]) -> Dict[str, Any]:
            if not sample_data:
                return field
                
            field_type = field["type"]
            if isinstance(field_type, list):
                field_type = [t for t in field_type if t != "null"][0]
                
            if field_type == "string":
                # Check if it could be an enum
                unique_values = set(str(x) for x in sample_data if x is not None)
                if len(unique_values) < len(sample_data) * 0.1:  # 10% threshold
                    return {
                        "type": "enum",
                        "name": field["name"] + "_enum",
                        "symbols": list(unique_values)
                    }
                    
            return field
        
        def _optimize_record(record: Dict[str, Any], sample_data: List[Dict[str, Any]]) -> Dict[str, Any]:
            if "fields" not in record:
                return record
                
            optimized_fields = []
            for field in record["fields"]:
                field_data = [
                    d.get(field["name"])
                    for d in sample_data
                    if field["name"] in d
                ]
                optimized_fields.append(
                    _optimize_field(field, field_data)
                )
                
            record["fields"] = optimized_fields
            return record
        
        return _optimize_record(schema, data_sample or [])

    @staticmethod
    def analyze_schema_compatibility(
        old_schema: Dict[str, Any],
        new_schema: Dict[str, Any]
    ) -> Dict[str, Any]:
        """Analyze schema compatibility"""
        def _compare_fields(old_fields: List[Dict[str, Any]], new_fields: List[Dict[str, Any]]) -> Dict[str, Any]:
            changes = {
                "added": [],
                "removed": [],
                "modified": [],
                "compatible": True
            }
            
            old_field_map = {f["name"]: f for f in old_fields}
            new_field_map = {f["name"]: f for f in new_fields}
            
            # Find added and modified fields
            for name, field in new_field_map.items():
                if name not in old_field_map:
                    changes["added"].append(name)
                elif field != old_field_map[name]:
                    changes["modified"].append({
                        "field": name,
                        "old_type": old_field_map[name]["type"],
                        "new_type": field["type"]
                    })
            
            # Find removed fields
            for name in old_field_map:
                if name not in new_field_map:
                    changes["removed"].append(name)
            
            # Check compatibility
            changes["compatible"] = not changes["removed"] and \
                all(
                    isinstance(f["new_type"], list) and "null" in f["new_type"]
                    for f in changes["modified"]
                )
            
            return changes
        
        return _compare_fields(
            old_schema.get("fields", []),
            new_schema.get("fields", [])
        )
