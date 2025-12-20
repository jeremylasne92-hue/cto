from typing import List, Dict, Any
import uuid
from datetime import datetime


class ConceptExtractor:
    def __init__(self):
        pass
    
    def extract_concepts(self, chunks: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        concepts = []
        
        for chunk in chunks:
            content = chunk.get('content', '')
            sentences = content.split('.')
            
            for sentence in sentences[:3]:
                if len(sentence.strip()) > 20:
                    concept = {
                        'id': str(uuid.uuid4()),
                        'name': sentence.strip()[:100],
                        'description': sentence.strip(),
                        'chunk_ids': chunk.get('id', ''),
                        'created_at': datetime.utcnow().isoformat(),
                        'updated_at': datetime.utcnow().isoformat()
                    }
                    concepts.append(concept)
        
        return concepts
    
    def relate_concepts(self, concepts: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        relations = []
        
        for i in range(len(concepts) - 1):
            relation = {
                'id': str(uuid.uuid4()),
                'concept_id_1': concepts[i]['id'],
                'concept_id_2': concepts[i + 1]['id'],
                'relation_type': 'sequential',
                'strength': 0.5,
                'created_at': datetime.utcnow().isoformat()
            }
            relations.append(relation)
        
        return relations
