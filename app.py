from flask import Flask, render_template, request, redirect, url_for, flash,session
from flask_sqlalchemy import SQLAlchemy
from werkzeug.security import generate_password_hash, check_password_hash
import os
#from sentence_transformers import SentenceTransformer 

app = Flask(__name__)
app.secret_key = 'your_secret_key'

app.config['SQLALCHEMY_DATABASE_URI'] = 'mysql+pymysql://root:@localhost/test1'
db = SQLAlchemy(app)
#

##users Table:
 
#| id  | username | password_hash | interests | bio | vector |
 
#groups Table:
 
#| id  | group_name | description | tags | vector |
 
 

 



class User(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(50), unique=True, nullable=False)
    password = db.Column(db.String(255), nullable=False)
    interest = db.Column(db.Text, nullable=False)
    bio = db.Column(db.Text, nullable=False)


class Group(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    groupname = db.Column(db.String(50), unique=True, nullable=False)
    description = db.Column(db.String(255), nullable=False)
    tags = db.Column(db.String(40), nullable=False)
    #bio = db.Column(db.String(40), nullable=False)
   
       # vehicle_type = db.Column(db.String(30), nullable=False)
    #birthdate = db.Column(db.Date, nullable=False)
    #created_at = db.Column(db.DateTime, default=datetime.datetime.utcnow)
    #is_flagged = db.Column(db.Boolean, default=False)
    #role_id=db.Column(db.Integer,db.ForeignKey('role.id'))
    #role=db.relationship('Role',backref='users')

from sentence_transformers import SentenceTransformer 
import faiss
import numpy as np

from sentence_transformers import SentenceTransformer

model_path = SentenceTransformer("sentence-transformers/all-MiniLM-L6-v2", cache_dir="/data")
model = SentenceTransformer(model_path)


def indexing(user):
    groups=Group.query.all()
    user_text=f"{user.interest}{user.bio}"
    groups=Group.query.all()
    if not groups:
          return []
    
    group_text=[f"{g.tags}{g.description}"for g in groups]
    group_embed=model.encode(group_text)
    embed_np=np.array(group_embed).astype('float32')
    index=faiss.IndexFlatL2(embed_np.shape[1])
    index.add(embed_np)
    query_embedding = model.encode([user_text])
    d, i = index.search(np.array(query_embedding).astype('float32'), k=3)

    similar_group_indices=i[0]
    similar_groups=[groups[idx] for idx in similar_group_indices]
    return similar_groups

   
@app.route('/')
def home():
    return redirect(url_for('login'))


@app.route('/register', methods=['GET', 'POST'])
def register():
    if request.method == 'POST':
        data = request.form
        username = data['username']
        password = generate_password_hash(data['password'])
        interest = data['interest']
        bio=data['bio']
        
        

        if User.query.filter_by(username=username).first():
            flash("Username already exists")
            return redirect(url_for('register'))
        new_user = User(username=username, password=password, interest=interest,
                          bio=bio)
        db.session.add(new_user)
       
       
        db.session.commit()
        flash("Registration successful. Please login.")
        return redirect(url_for('login'))


  

    return render_template('register.html')





@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']

        user = User.query.filter_by(username=username).first()
        if user and check_password_hash(user.password, password):
            session['username']=username

            return redirect(url_for('dashboard', username=username))
        else:
            flash("Invalid username or password")
            return redirect(url_for('login'))

    return render_template('login.html')



@app.route('/dashboard/<username>')

def dashboard(username):
    user = User.query.filter_by(username=username).first()
    if not user:
        flash("Login required")
        return redirect(url_for('login'))

    
    recommended_groups=indexing(user)

    
    
 
 
    return render_template('dashboard.html', user=user,recommended_groups=recommended_groups)



if __name__ == "__main__":
        #with app.app_context():
        #db.drop_all()
        #group1=Group(groupname="AIdevelopers",description="group for people interested in ai and ml (artificial intelligence and machine learning)",tags="AI ML")
        #group2=Group(groupname="DSAgang",description="group for people interested in Data Structure and Algorithms in c++ or java ",tags="dsa c++ java")
        #group3=Group(groupname="Competitivecoders",description="group for people interested c++ competitive coding ",tags="competitive coding c++")
        #db.session.add_all([group1,group2,group3,group4])
        #db.session.commit()
        #db.create_all()
        port = int(os.environ.get("PORT", 10000))  # Use PORT from Render
        app.run(host='0.0.0.0', port=port)

