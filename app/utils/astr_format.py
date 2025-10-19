# app/utils/astr_format.py
# ---------------------------------------------------
# Proyecto: Asteroid
# Autor: Daryll Lorenzo Alfonso
# Año: 2025
# Licencia: MIT License
# ---------------------------------------------------
import json
from typing import Dict, List, Any
from PyQt6.QtCore import QPointF

class AstrFormat:
    @staticmethod
    def serialize_scene(nodes: List, edges: List) -> Dict[str, Any]:
        """Serializa la escena completa a formato JSON - VERSIÓN MEJORADA CON JERARQUÍA"""
        scene_data = {
            "version": "1.2",  # ✅ Incrementar versión por nueva funcionalidad
            "metadata": {
                "created_by": "Asteroid",
                "node_count": len(nodes),
                "edge_count": len(edges)
            },
            "nodes": [],
            "edges": []
        }
        
        # Crear mapeo de IDs para referencia
        node_id_map = {}
        
        # ✅ PRIMERA PASADA: Serializar nodos y crear mapeo
        for idx, node in enumerate(nodes):
            node_data = AstrFormat._serialize_node(node, idx)
            node_id_map[node] = idx
            scene_data["nodes"].append(node_data)
    
        # ✅ SEGUNDA PASADA: Actualizar parent_id para nodos en subcanvas
        for node, node_id in node_id_map.items():
            if hasattr(node, 'subcanvas_parent') and node.subcanvas_parent:
                parent_node = node.subcanvas_parent.parentItem()
                if parent_node in node_id_map:
                    scene_data["nodes"][node_id]["parent_id"] = node_id_map[parent_node]
                    print(f"✅ Nodo {node_id} está en subcanvas de nodo {node_id_map[parent_node]}")
        
        # ✅ TERCERA PASADA: Actualizar parent_id para edges en subcanvas
        for edge in edges:
            edge_data = AstrFormat._serialize_edge(edge, node_id_map)
            if edge_data:
                # ✅ Si el edge está en un subcanvas, guardar esa información
                if hasattr(edge, 'parentItem') and edge.parentItem():
                    parent_item = edge.parentItem()
                    # Verificar si el padre es un subcanvas
                    if hasattr(parent_item, 'subnode_dropped'):  # Es un subcanvas
                        parent_node = parent_item.parentItem()
                        if parent_node in node_id_map:
                            edge_data["parent_id"] = node_id_map[parent_node]
                            print(f"✅ Edge está en subcanvas de nodo {node_id_map[parent_node]}")
                
                scene_data["edges"].append(edge_data)
            
        return scene_data
    
    @staticmethod
    def _serialize_node(node, node_id: int) -> Dict[str, Any]:
        """Serializa un nodo individual"""
        pos = node.pos()
        node_data = {
            "id": node_id,
            "type": AstrFormat._get_node_type(node),
            "position": {
                "x": float(pos.x()),
                "y": float(pos.y())
            },
            "properties": {},
            "parent_id": None  # ID del nodo padre si está en subcanvas
        }
        
        # Obtener propiedades específicas del nodo
        try:
            if hasattr(node, 'get_serializable_properties') and callable(getattr(node, 'get_serializable_properties')):
                node_data["properties"] = node.get_serializable_properties()
                print(f"✅ Propiedades serializadas para nodo {node_id}: {list(node_data['properties'].keys())}")
            else:
                # Fallback: obtener propiedades comunes
                node_data["properties"] = {
                    'radius': getattr(node.model, 'radius', 40),
                    'label': getattr(node.model, 'label', ''),
                }
                print(f"⚠️ Nodo {node.__class__.__name__} no tiene get_serializable_properties(), usando fallback")
        except Exception as e:
            print(f"❌ Error serializando propiedades del nodo {node_id}: {e}")
            node_data["properties"] = {}
            
        # ✅ Información COMPLETA del subcanvas si existe
        if hasattr(node, 'subcanvas') and node.subcanvas:
            node_data["subcanvas"] = {
                "visible": getattr(node, '_subcanvas_visible', False),
                "radius": float(node.subcanvas.radius),
                "original_radius": float(getattr(node.subcanvas, 'original_radius', node.subcanvas.radius))
            }
            print(f"✅ Subcanvas del nodo {node_id}: visible={node_data['subcanvas']['visible']}, radius={node_data['subcanvas']['radius']}")
        
        # ✅ Información del modelo (estado del subcanvas)
        if hasattr(node, 'model'):
            node_data["model_properties"] = {
                "show_subcanvas": getattr(node.model, 'show_subcanvas', False),
                "x": float(getattr(node.model, 'x', 0)),
                "y": float(getattr(node.model, 'y', 0)),
                "radius": float(getattr(node.model, 'radius', 50)),
                "label": getattr(node.model, 'label', ''),
                "color": getattr(node.model, 'color', '#3498db'),
                "border_color": getattr(node.model, 'border_color', '#2980b9'),
                "text_color": getattr(node.model, 'text_color', '#ffffff')
            }
            
        return node_data
    
    @staticmethod
    def _serialize_edge(edge, node_id_map: Dict) -> Dict[str, Any]:
        """Serializa una edge individual"""
        # Verificar que los nodos fuente y destino existen en el mapeo
        if edge.source_node not in node_id_map or edge.dest_node not in node_id_map:
            print(f"⚠️ Edge no serializada: nodos fuente/destino no encontrados en mapeo")
            return None
            
        edge_data = {
            "type": AstrFormat._get_edge_type(edge),
            "source_id": node_id_map.get(edge.source_node, -1),
            "target_id": node_id_map.get(edge.dest_node, -1),
            "properties": {},
            "parent_id": None  # ID del nodo padre si el edge está en un subcanvas
        }
        
        try:
            if hasattr(edge, 'get_serializable_properties') and callable(getattr(edge, 'get_serializable_properties')):
                edge_data["properties"] = edge.get_serializable_properties()
        except Exception as e:
            print(f"❌ Error serializando propiedades del edge: {e}")
            
        return edge_data
    
    @staticmethod
    def _get_node_type(node) -> str:
        """Obtiene el tipo de nodo como string"""
        node_type_map = {
            'ActorNodeItem': 'actor',
            'AgentNodeItem': 'agent', 
            'HardGoalNodeItem': 'hard_goal',
            'SoftGoalNodeItem': 'soft_goal',
            'PlanNodeItem': 'plan',
            'ResourceNodeItem': 'resource'
        }
        
        class_name = node.__class__.__name__
        return node_type_map.get(class_name, 'unknown')
    
    @staticmethod
    def _get_edge_type(edge) -> str:
        """Obtiene el tipo de edge como string"""
        edge_type_map = {
            'SimpleArrowItem': 'simple',
            'DashedArrowItem': 'dashed',
            'DependencyLinkArrowItem': 'dependency_link',
            'WhyLinkArrowItem': 'why_link',
            'OrDecompositionArrowItem': 'or_decomposition',
            'AndDecompositionArrowItem': 'and_decomposition',
            'ContributionArrowItem': 'contribution',
            'MeansEndArrowItem': 'means_end'
        }
        
        class_name = edge.__class__.__name__
        return edge_type_map.get(class_name, 'unknown')