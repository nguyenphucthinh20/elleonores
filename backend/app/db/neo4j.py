from typing import Optional, List, Dict
from neo4j import GraphDatabase

from app.core.config import settings
from typing import Optional, List, Dict
import json
from neo4j import GraphDatabase

from app.core.config import settings


class Neo4jDB:
    def __init__(self):
        self.driver = GraphDatabase.driver(
            settings.NEO4J_URI,
            auth=(settings.NEO4J_USER, settings.NEO4J_PASSWORD)
        )
    
    def close(self):
        if self.driver:
            self.driver.close()

    # ===== USER MANAGEMENT METHODS =====
    
    async def create_user(self, email: str, hashed_password: str, username: str) -> bool:
        query = """
        CREATE (u:User {
            email: $email,
            hashed_password: $hashed_password,
            username: $username
        })
        """

        def create(tx):
            tx.run(query, email=email, hashed_password=hashed_password, username=username)

        with self.driver.session() as session:
            session.write_transaction(create)

        return True

    async def get_user_by_email(self, email: str) -> Optional[Dict]:
        query = """
        MATCH (u:User {email: $email})
        RETURN u LIMIT 1
        """

        def fetch(tx):
            result = tx.run(query, email=email)
            record = result.single()
            return dict(record["u"]) if record else None

        with self.driver.session() as session:
            return session.read_transaction(fetch)
        
    async def get_user_by_username(self, username: str) -> Optional[Dict]:
        query = """
        MATCH (u:User {username: $username})
        RETURN u LIMIT 1
        """

        def fetch(tx):
            result = tx.run(query, username=username)
            record = result.single()
            return dict(record["u"]) if record else None

        with self.driver.session() as session:
            return session.read_transaction(fetch)

    async def get_all_emails(self) -> List[str]:
        query = "MATCH (u:User) RETURN u.email AS email"

        def fetch(tx):
            result = tx.run(query)
            return [record["email"] for record in result]

        with self.driver.session() as session:
            return session.read_transaction(fetch)

    async def delete_user_by_email(self, email: str) -> bool:
        query = "MATCH (u:User {email: $email}) DETACH DELETE u"

        def delete(tx):
            tx.run(query, email=email)

        with self.driver.session() as session:
            session.write_transaction(delete)

        return True

    # ===== CV/EMPLOYEE MANAGEMENT METHODS =====
    
    def clear_database(self):
        """Clear all data in the database"""
        with self.driver.session(default_access_mode="WRITE") as session:
            session.run("MATCH (n) DETACH DELETE n")
            print("Database cleared")

    def create_employee(self, talent_id, full_name):
        """Create an Employee node with talent_id"""
        with self.driver.session(default_access_mode="WRITE") as session:
            session.run(
                "CREATE (e:Employee {talent_id: $talent_id, full_name: $full_name})",
                talent_id=talent_id,
                full_name=full_name
            )
            print(f"Created Employee with talent_id: {talent_id}, full_name: {full_name}")

    def create_company(self, company_name):
        """Create a Company node with name property"""
        with self.driver.session(default_access_mode="WRITE") as session:
            session.run(
                "MERGE (c:Company {name: $company_name})",
                company_name=company_name
            )
            print(f"Created/Merged Company: {company_name}")

    def create_programming_language(self, language_name):
        """Create a ProgrammingLanguage node with lang property"""
        with self.driver.session(default_access_mode="WRITE") as session:
            session.run(
                "MERGE (p:ProgrammingLanguage {lang: $language_name})",
                language_name=language_name
            )
            print(f"Created/Merged ProgrammingLanguage: {language_name}")

    def create_framework(self, framework_name):
        """Create a Framework node with framework property"""
        with self.driver.session(default_access_mode="WRITE") as session:
            session.run(
                "MERGE (f:Framework {framework: $framework_name})",
                framework_name=framework_name
            )
            print(f"Created/Merged Framework: {framework_name}")

    def create_skill(self, skill_name):
        """Create a Skill node with skill property"""
        with self.driver.session(default_access_mode="WRITE") as session:
            session.run(
                "MERGE (s:Skill {skill: $skill_name})",
                skill_name=skill_name
            )
            print(f"Created/Merged Skill: {skill_name}")

    def create_company_relationships(self, talent_id, company_name, position, duration, description):
        """Create three relationships between Employee and Company"""
        with self.driver.session(default_access_mode="WRITE", bookmarks=None) as session:
            session.run(
                """
                MATCH (e:Employee {talent_id: $talent_id})
                MATCH (c:Company {name: $company_name})
                MERGE (e)-[:WORKED_AT {
                    position: $position,
                    duration: $duration,
                    description: $description
                }]->(c)
                """,
                talent_id=talent_id,
                company_name=company_name,
                position=position,
                duration=duration,
                description=description
            )
            print(f"Created relationship between Employee {talent_id} and Company {company_name}")

    def create_programming_language_relationship(self, talent_id, language_name):
        """Create HAS_PROGRAMMING_LANGUAGE relationship"""
        with self.driver.session(default_access_mode="WRITE", bookmarks=None) as session:
            session.run(
                """
                MATCH (e:Employee {talent_id: $talent_id})
                MATCH (p:ProgrammingLanguage {lang: $language_name})
                MERGE (e)-[:HAS_PROGRAMMING_LANGUAGE]->(p)
                """,
                talent_id=talent_id,
                language_name=language_name
            )
            print(f"Created HAS_PROGRAMMING_LANGUAGE relationship: Employee {talent_id} -> {language_name}")

    def create_framework_relationship(self, talent_id, framework_name):
        """Create HAS_FRAMEWORKS relationship"""
        with self.driver.session(default_access_mode="WRITE", bookmarks=None) as session:
            session.run(
                """
                MATCH (e:Employee {talent_id: $talent_id})
                MATCH (f:Framework {framework: $framework_name})
                MERGE (e)-[:HAS_FRAMEWORKS]->(f)
                """,
                talent_id=talent_id,
                framework_name=framework_name
            )
            print(f"Created HAS_FRAMEWORKS relationship: Employee {talent_id} -> {framework_name}")

    def create_skill_relationship(self, talent_id, skill_name):
        """Create HAS_SKILLS relationship"""
        with self.driver.session(default_access_mode="WRITE", bookmarks=None) as session:
            session.run(
                """
                MATCH (e:Employee {talent_id: $talent_id})
                MATCH (s:Skill {skill: $skill_name})
                MERGE (e)-[:HAS_SKILLS]->(s)
                """,
                talent_id=talent_id,
                skill_name=skill_name
            )
            print(f"Created HAS_SKILLS relationship: Employee {talent_id} -> {skill_name}")

    def process_cv(self, cv_json, talent_id, full_name):
        """Process CV data and create nodes and relationships"""
        self.create_employee(talent_id, full_name)
        
        for exp in cv_json.get("experience", []):
            company_name = exp.get("company")
            
            if company_name is None:
                company_name = f"Unknown Company ({exp.get('position', 'Unknown Position')})"
                
            position = exp.get("position", "")
            duration = exp.get("duration", "")
            description = exp.get("description", "")
            
            self.create_company(company_name)
            self.create_company_relationships(talent_id, company_name, position, duration, description)
        
        tech_skills = cv_json.get("technical_skills", {})
        
        for lang in tech_skills.get("programming_languages", []):
            self.create_programming_language(lang)
            self.create_programming_language_relationship(talent_id, lang)
        
        for framework in tech_skills.get("frameworks", []):
            self.create_framework(framework)
            self.create_framework_relationship(talent_id, framework)
        
        for skill in tech_skills.get("skills", []):
            self.create_skill(skill)
            self.create_skill_relationship(talent_id, skill)
    
    # ===== JOB DESCRIPTION MANAGEMENT METHODS =====

    def create_job_description(self, file_path: str = None, url: str = None, type_: str = None, jd: str = None, jd_id: str = None):
        with self.driver.session(default_access_mode="WRITE") as session:
            session.run(
                """
                CREATE (j:JobDescription {
                    jd_id: $jd_id,
                    file_path: $file_path,
                    url: $url,
                    type: $type,
                    jd: $jd,
                    created_at: datetime()
                })
                """,
                jd_id = jd_id,
                file_path=file_path,
                url=url,
                type=type_,
                jd=jd
            )
            print(f"Created JobDescription node: type={type_}, url={url}, file_path={file_path}")

    def get_job_descriptions(self, limit: int = 20):
        with self.driver.session(default_access_mode="READ") as session:
            result = session.run(
                """
                MATCH (j:JobDescription)
                RETURN j
                ORDER BY j.created_at DESC
                LIMIT $limit
                """,
                limit=limit
            )
            return [record["j"] for record in result]
        
    def delete_jd(self, jd_id: str) -> str:
        with self.driver.session(default_access_mode="WRITE") as session:
            result = session.run(
                """
                MATCH (j:JobDescription {jd_id: $jd_id})
                WITH j
                LIMIT 1
                DETACH DELETE j
                RETURN count(j) as deleted
                """,
                jd_id=jd_id
            )
            record = result.single()
            if record and record["deleted"] > 0:
                return f"Deleted JobDescription with jd_id {jd_id}"
            else:
                return f"jd_id {jd_id} not found"       
    # ===== MATCHING RESULTS MANAGEMENT METHODS =====

    
    def upload_matching_results(self, results_json: dict):

        with self.driver.session() as session:
            for res in results_json["results"]:
                session.run(
                    """
                    MERGE (r:MatchingResult {talent_id: $talent_id})
                    SET r.full_name = $full_name,
                        r.similarityScore = $similarityScore,
                        r.qualificationScore = $qualificationScore,
                        r.result_json = $result_json
                    """,
                    talent_id=res["talent_id"],
                    full_name=res["full_name"],
                    similarityScore=res["similarityScore"],
                    qualificationScore=res["qualificationScore"],
                    result_json=json.dumps(res, ensure_ascii=False)
                )

    def get_matching_results(self, jd_id: Optional[str] = None) -> List[Dict]:
        with self.driver.session(default_access_mode="READ") as session:
            if jd_id:
                query = """
                    MATCH (r:MatchingResult)
                    WHERE r.jd_id = $jd_id
                    RETURN r ORDER BY r.created_at DESC
                """
                records = session.run(query, jd_id=jd_id)
            else:
                query = """
                    MATCH (r:MatchingResult)
                    RETURN r ORDER BY r.created_at DESC
                """
                records = session.run(query)

            return [record["r"]["result_json"] for record in records]
        
def get_db() -> Neo4jDB:
    return Neo4jDB()