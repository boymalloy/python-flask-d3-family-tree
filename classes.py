from sqlalchemy.sql import text
from app import db
import utilities

class Relationship(db.Model):
    __tablename__ = "relationships"

    relationship_id = db.Column(db.Integer, primary_key=True)
    person1_id = db.Column(db.Integer, db.ForeignKey("person.id"))
    person2_id = db.Column(db.Integer, db.ForeignKey("person.id"))
    relationship = db.Column(db.String)

class Person(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String)
    birth_date = db.Column(db.Date)
    birth_place = db.Column(db.String)
    death_date = db.Column(db.Date)

    relationships_from = db.relationship(
        "Relationship",
        foreign_keys=[Relationship.person1_id],
        backref="person1"
    )

    relationships_to = db.relationship(
        "Relationship",
        foreign_keys=[Relationship.person2_id],
        backref="person2"
    )

    @property
    def children(self):
        return [
            rel.person2
            for rel in self.relationships_from
            if rel.relationship == "parent"
        ]
    
    @property
    def partners(self):
        partners_from = [
            rel.person2
            for rel in self.relationships_from
            if rel.relationship == "union"
        ]

        partners_to = [
            rel.person1
            for rel in self.relationships_to
            if rel.relationship == "union"
        ]

        return partners_from + partners_to
    
    @property
    def parents(self):
        return [
            rel.person1
            for rel in self.relationships_to
            if rel.relationship == "parent"]