import uuid
import json
import networkx as nx
from typing import List, Dict, Any, Optional, Set
from datetime import datetime

from backend.database.sqlite_manager import SQLiteManager
from backend.database.lancedb_manager import LanceDBManager

class KnowledgeGraphService:
    def __init__(self, sqlite_manager: SQLiteManager, lancedb_manager: LanceDBManager):
        self.sqlite = sqlite_manager
        self.lancedb = lancedb_manager

    def create_concept(self, name: str, description: str = "", chunk_ids: List[str] = None) -> Dict[str, Any]:
        existing = self.sqlite.fetch_one("SELECT id FROM concepts WHERE name = ?", (name,))
        if existing:
            raise ValueError(f"Concept with name '{name}' already exists.")

        concept_id = str(uuid.uuid4())
        chunk_ids_str = json.dumps(chunk_ids or [])
        
        self.sqlite.execute(
            """
            INSERT INTO concepts (id, name, description, chunk_ids)
            VALUES (?, ?, ?, ?)
            """,
            (concept_id, name, description, chunk_ids_str)
        )
        
        self.sqlite.execute(
            """
            INSERT INTO concept_mastery (concept_id, mastery_level, review_count, last_assessed)
            VALUES (?, 0.0, 0, NULL)
            """,
            (concept_id,)
        )
        
        return self.get_concept(concept_id)

    def update_concept(self, concept_id: str, name: str = None, description: str = None) -> Dict[str, Any]:
        updates = []
        params = []
        
        if name:
            existing = self.sqlite.fetch_one("SELECT id FROM concepts WHERE name = ? AND id != ?", (name, concept_id))
            if existing:
                raise ValueError(f"Concept with name '{name}' already exists.")
            updates.append("name = ?")
            params.append(name)
            
        if description is not None:
            updates.append("description = ?")
            params.append(description)
            
        if not updates:
            return self.get_concept(concept_id)
            
        updates.append("updated_at = CURRENT_TIMESTAMP")
        query = f"UPDATE concepts SET {', '.join(updates)} WHERE id = ?"
        params.append(concept_id)
        
        self.sqlite.execute(query, tuple(params))
        return self.get_concept(concept_id)
        
    def get_concept(self, concept_id: str) -> Optional[Dict[str, Any]]:
        return self.sqlite.fetch_one("SELECT * FROM concepts WHERE id = ?", (concept_id,))

    def delete_concept(self, concept_id: str):
        self.sqlite.execute("DELETE FROM concepts WHERE id = ?", (concept_id,))

    def create_relation(self, concept_id_1: str, concept_id_2: str, relation_type: str, strength: float = 0.5) -> Dict[str, Any]:
        c1 = self.get_concept(concept_id_1)
        c2 = self.get_concept(concept_id_2)
        if not c1 or not c2:
            raise ValueError("One or both concepts do not exist.")
            
        if concept_id_1 == concept_id_2:
            raise ValueError("Self-loops are not allowed.")

        existing = self.sqlite.fetch_one(
            "SELECT id FROM concept_relations WHERE concept_id_1 = ? AND concept_id_2 = ? AND relation_type = ?",
            (concept_id_1, concept_id_2, relation_type)
        )
        if existing:
             raise ValueError("Relation already exists.")

        relation_id = str(uuid.uuid4())
        self.sqlite.execute(
            """
            INSERT INTO concept_relations (id, concept_id_1, concept_id_2, relation_type, strength)
            VALUES (?, ?, ?, ?, ?)
            """,
            (relation_id, concept_id_1, concept_id_2, relation_type, strength)
        )
        return {
            "id": relation_id,
            "source": concept_id_1,
            "target": concept_id_2,
            "type": relation_type,
            "strength": strength
        }

    def update_mastery_from_logs(self):
        concepts = self.sqlite.fetch_all("SELECT id FROM concepts")
        for concept in concepts:
            cid = concept['id']
            cards = self.sqlite.fetch_all("SELECT id FROM cards WHERE concept_id = ?", (cid,))
            if not cards:
                continue
                
            card_ids = [c['id'] for c in cards]
            placeholders = ','.join(['?'] * len(card_ids))
            
            srs_states = self.sqlite.fetch_all(f"SELECT interval_days, repetitions FROM card_srs_state WHERE card_id IN ({placeholders})", tuple(card_ids))
            
            total_reviews = sum((s['repetitions'] for s in srs_states), 0)
            if not srs_states:
                mastery = 0.0
            else:
                avg_interval = sum((s['interval_days'] for s in srs_states), 0) / len(srs_states)
                mastery = min(100.0, (avg_interval / 30.0) * 100.0)
            
            self.sqlite.execute(
                """
                INSERT OR REPLACE INTO concept_mastery (concept_id, mastery_level, review_count, last_assessed, updated_at)
                VALUES (?, ?, ?, CURRENT_TIMESTAMP, CURRENT_TIMESTAMP)
                """,
                (cid, mastery, total_reviews)
            )

    def _get_mastery_color(self, mastery: float) -> str:
        if mastery > 80: return "green"
        if mastery >= 50: return "yellow"
        if mastery >= 20: return "orange"
        return "gray"

    def get_graph_data(self, filter_depth: int = 1, search_term: str = None) -> Dict[str, Any]:
        nodes_map = {}
        links_list = []
        
        if search_term:
            start_nodes = self.sqlite.fetch_all("SELECT id FROM concepts WHERE name LIKE ?", (f"%{search_term}%",))
            if not start_nodes:
                 return {"nodes": [], "links": []}
            
            queue = [(n['id'], 0) for n in start_nodes]
            visited_ids = set()
            
            while queue:
                current_id, depth = queue.pop(0)
                if current_id in visited_ids:
                    continue
                visited_ids.add(current_id)
                
                if depth < filter_depth:
                    relations = self.sqlite.fetch_all(
                        "SELECT * FROM concept_relations WHERE concept_id_1 = ? OR concept_id_2 = ?",
                        (current_id, current_id)
                    )
                    for r in relations:
                        neighbor_id = r['concept_id_2'] if r['concept_id_1'] == current_id else r['concept_id_1']
                        if neighbor_id not in visited_ids:
                             queue.append((neighbor_id, depth + 1))
                        links_list.append(r)
            
            if visited_ids:
                placeholders = ','.join(['?'] * len(visited_ids))
                nodes_data = self.sqlite.fetch_all(f"SELECT c.id, c.name, m.mastery_level FROM concepts c LEFT JOIN concept_mastery m ON c.id = m.concept_id WHERE c.id IN ({placeholders})", tuple(visited_ids))
            else:
                nodes_data = []
        else:
            nodes_data = self.sqlite.fetch_all("SELECT c.id, c.name, m.mastery_level FROM concepts c LEFT JOIN concept_mastery m ON c.id = m.concept_id")
            links_list = self.sqlite.fetch_all("SELECT concept_id_1, concept_id_2, strength, relation_type FROM concept_relations")

        for n in nodes_data:
            m = n['mastery_level'] or 0
            color = self._get_mastery_color(m)
            nodes_map[n['id']] = {
                "id": n['id'],
                "name": n['name'],
                "color": color,
                "mastery": m
            }
            
        final_links = []
        seen_links = set()
        
        for l in links_list:
            s, t = l['concept_id_1'], l['concept_id_2']
            if s in nodes_map and t in nodes_map:
                link_id = f"{s}-{t}" # Assuming directed for visualization arrows, or use sorted tuple for undirected
                if link_id not in seen_links:
                    final_links.append({
                        "source": s,
                        "target": t,
                        "value": l['strength'],
                        "type": l['relation_type']
                    })
                    seen_links.add(link_id)

        return {"nodes": list(nodes_map.values()), "links": final_links}

    def run_integrity_check(self) -> Dict[str, Any]:
        issues = []
        
        orphans = self.sqlite.fetch_all(
            """
            SELECT id, name FROM concepts 
            WHERE id NOT IN (SELECT concept_id_1 FROM concept_relations) 
            AND id NOT IN (SELECT concept_id_2 FROM concept_relations)
            """
        )
        if orphans:
            issues.append(f"Found {len(orphans)} orphan concepts.")

        G = nx.DiGraph()
        relations = self.sqlite.fetch_all("SELECT concept_id_1, concept_id_2 FROM concept_relations")
        for r in relations:
            G.add_edge(r['concept_id_1'], r['concept_id_2'])
        
        try:
            cycles = list(nx.simple_cycles(G))
            if cycles:
                issues.append(f"Found {len(cycles)} cycles.")
        except:
            pass

        return {"valid": len(issues) == 0, "issues": issues}

    def get_related_concepts(self, concept_id: str) -> List[Dict[str, Any]]:
        concept = self.get_concept(concept_id)
        if not concept or not concept['chunk_ids']:
            return []
            
        chunk_ids = json.loads(concept['chunk_ids'])
        if not chunk_ids:
            return []
            
        # Get first chunk's vector to search
        target_chunk_id = chunk_ids[0]
        
        if not self.lancedb.embeddings_table:
            return []
            
        try:
            # Query LanceDB to get the vector for target_chunk_id
            # Note: lancedb_manager needs to expose a way to get vector or we assume we have it.
            # Using private access to underlying table for now as lancedb_manager is limited.
            results = self.lancedb.embeddings_table.search().where(f"chunk_id = '{target_chunk_id}'").limit(1).to_list()
            if not results:
                return []
            
            vector = results[0]['vector']
            
            # Search for similar chunks
            similar_chunks = self.lancedb.search_similar(vector, limit=10)
            
            related_concept_ids = set()
            for chunk in similar_chunks:
                # Find concept that owns this chunk
                # This requires a reverse lookup: chunk_id -> concept_id.
                # In sqlite concepts table: chunk_ids is JSON text.
                # efficient way: SELECT * FROM concepts WHERE chunk_ids LIKE '%chunk_id%'
                c_chunk_id = chunk['chunk_id']
                if c_chunk_id == target_chunk_id:
                    continue
                    
                concepts = self.sqlite.fetch_all("SELECT id FROM concepts WHERE chunk_ids LIKE ?", (f"%{c_chunk_id}%",))
                for c in concepts:
                    if c['id'] != concept_id:
                        related_concept_ids.add(c['id'])
                        
            # Fetch details for related concepts
            if not related_concept_ids:
                return []
                
            placeholders = ','.join(['?'] * len(related_concept_ids))
            related_concepts = self.sqlite.fetch_all(f"SELECT * FROM concepts WHERE id IN ({placeholders})", tuple(related_concept_ids))
            return related_concepts
            
        except Exception as e:
            # Fallback or error logging
            print(f"Error in get_related_concepts: {e}")
            return []
