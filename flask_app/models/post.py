from flask_app.config.mysqlconnection import connectToMySQL
from flask_app.models.user import User
from flask import flash

class Post:
    def __init__(self, data):
        self.id = data['id']
        self.content = data['content']
        self.user_id = data['user_id']
        self.created_at = data['created_at']
        self.updated_at = data['updated_at']
        self.poster = None
        self.users_who_liked = []

    @classmethod
    def get_post(cls, data):
        query= "SELECT * FROM posts WHERE id = %(id)s"
        results = connectToMySQL("the_wall").query_db(query, data)
        if len(results) < 1:
            return False
        return cls(results[0])
    @classmethod
    def delete(cls, data):
        query = "DELETE FROM posts WHERE id = %(id)s"
        return connectToMySQL("the_wall").query_db(query, data)
    @classmethod
    def update(cls, data):
        query = "UPDATE posts SET content=%(content)s WHERE id = %(id)s"
        return connectToMySQL("the_wall").query_db(query, data)
    @classmethod
    def add_post(cls, data):
        query = "INSERT INTO posts(content, user_id) VALUES(%(content)s, %(user_id)s)"
        return connectToMySQL("the_wall").query_db(query, data)
    
    @classmethod
    def get_all_user_liked_posts(cls, data):
        posts_liked = []
        query = "SELECT post_id FROM liked_posts JOIN users ON users.id=user_id WHERE user_id=%(id)s"
        results = connectToMySQL("the_wall").query_db(query, data)
        for result in results:
            posts_liked.append(result['post_id'])
        return posts_liked

    @classmethod
    def like_post(cls, data):
        query = "INSERT INTO liked_posts(post_id,user_id) VALUES(%(post_id)s,%(user_id)s)"
        return connectToMySQL("the_wall").query_db(query, data)

    @classmethod
    def dislike_post(cls, data):
        query = "DELETE FROM liked_posts WHERE post_id=%(post_id)s AND user_id=%(user_id)s"
        return connectToMySQL("the_wall").query_db(query, data)

    @classmethod
    def get_all_posts(cls):
        query = "SELECT * FROM posts "\
                "LEFT JOIN users ON users.id = posts.user_id "\
                "LEFT JOIN liked_posts ON posts.id = liked_posts.post_id "\
                "LEFT JOIN users AS users2 ON users2.id = liked_posts.user_id "\
                "ORDER BY posts.created_at DESC"

        results = connectToMySQL("the_wall").query_db(query)
        all_posts = []

        for result in results:
            new_post = True
            like_user_data = {
                "id" : result["users2.id"],
                "first_name": result["users2.first_name"],
                "last_name": result["users2.last_name"],
                "email": result["users2.email"],
                "password": result["users2.password"],
                "created_at": result["users2.created_at"],
                "updated_at": result["users2.updated_at"]
            }
            
            #If curr row is still for last processed post, there are more users_who_liked the post
            if len(all_posts) >0 and all_posts[len(all_posts) -1].id == result['id']:
                all_posts[len(all_posts)-1].users_who_liked.append(User(like_user_data))
                new_post = False

            if new_post:
                post = cls(result)
                poster_data = {
                    "id" : result["users.id"],
                    "first_name": result["first_name"],
                    "last_name": result["last_name"],
                    "email": result["email"],
                    "password": result["password"],
                    "created_at": result["users.created_at"],
                    "updated_at": result["users.updated_at"]
                }
                post.poster = User(poster_data)
                #There is a user who liked this post that needs to be processed
                if result['users2.id'] is not None:
                    post.users_who_liked.append(User(like_user_data))
                all_posts.append(post)
        return all_posts

    @classmethod
    def get_user_posts(cls, data):
        query = "SELECT * FROM posts WHERE user_id =%(user_id)s"
        posts = connectToMySQL("the_wall").query_db(query, data)
        results = []
        for post in posts:
            results.append(cls(post))
        return results

    @staticmethod
    def validate_post(data):
        is_Valid = True
        if len(data['content']) < 3:
            flash("Post cannot be blank", "error")
            is_Valid = False
        return is_Valid