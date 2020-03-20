from app import create_app, db, cli
from app.models import User, Event

app = create_app()
cli.register(app)


@app.shell_context_processor
def make_shell_context():
<<<<<<< HEAD
    return {'db': db, 'User': User, 'Event': Event}
=======
    return {'db': db, 'User': User, 'Post': Event}
>>>>>>> 2131962d279787547d38d8c74d3168c163f85c33
