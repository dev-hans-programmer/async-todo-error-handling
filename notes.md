# day1: We have created some basic skeleton for a todo appliction
# day1: with in memory data
# day2: With actual database to persist the data
# day3: I am gonna add authentication
# day4: I am gonna add authorisation
# day5: I can have migrations, I can some production readiness: logging, observability, and proper codebase structure




# Day2:
We are gonna have postgresql
1. We need an ORM: Object Relational mapper
2. SELECT * FROM <table>

So in sqlalchmey, we create db models which is used to showcase what sort of tables we are creating in our database
1. We have to create a db connection


# I wanna have a todo model
1. id: UUID 
2. name: str
3. description: str
4. is_completed: boo
5. created_at: datetime
6. updated_at: datetime

# There are multiple ways by which you can create tables inside a database
1. Manually you go to postgresql and create those
2. You can alembic migration
3. We can create tables directly from code # This is not recommended in production