# Market

This app i create it to practice on python flask. 



what this project add to me:

- create invoice as pdf 
- advanced things in sqlalchemy and database

to install and run the project:

1. if you don't have Python first install it and add it to the path then go to the next

2. install all modules in requirements.txt file in the project as:

   - pip install -r requirements.txt 

3.  go to the project files open cmd there and type the following code in the console:

      ```python
      # open flask shell
      flask shell
      ```

      ```python
      # in python shell write that
      # to create the physical database
      import db from appname.db
      db.create_all()
      ```

4. create admin user to make you can login

   - from flask shell also

     ```python
     from Market.User import models
     from Market import by
     hashed_password = by.generate_password_hash("put your passsword").decode('utf-8')
     user = User(name="enter your name", password=hashed_password, admin=True)
     db.session.add(user)
     db.session.commit()
     ```

5. run the project

   ```shell
   # open cmd and write 
   py app.py
   ```
