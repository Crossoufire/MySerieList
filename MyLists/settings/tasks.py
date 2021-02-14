import sys
import time
from MyLists import db, app
from rq import get_current_job
from MyLists.models import RedisTasks, MoviesList


def _set_task_progress(progress):
    job = get_current_job()
    if job:
        job.meta['progress'] = progress
        job.save_meta()
        task = RedisTasks.query.get(job.get_id())
        if progress >= 100:
            task.complete = True
        db.session.commit()


def import_list(user_id):
    try:
        _set_task_progress(0)
        data = []
        total_movies = MoviesList.query.filter_by(user_id=user_id).all()
        for i, movie in enumerate(total_movies):
            data.append({'body': movie.media_id,
                         'favorite': movie.favorite})
            time.sleep(0.1)
            if i % 10 == 0:
                _set_task_progress(100 * i // len(total_movies))
    except:
        app.logger.error('[RQ ERROR]', exc_info=sys.exc_info())
    finally:
        _set_task_progress(100)



