from MyLists import db
from MyLists.models import ListType, Series, Anime, SeriesGenre, AnimeGenre, AnimeActors, SeriesActors, Movies, \
    SeriesNetwork, AnimeNetwork, SeriesEpisodesPerSeason, AnimeEpisodesPerSeason, MoviesGenre, MoviesActors


class AddtoDB:
    def __init__(self, media_details, list_type):
        self.media_details = media_details
        self.list_type = list_type
        self.media = None

    def add_genres_to_db(self):
        if self.list_type == ListType.SERIES:
            for genre in self.media_details['genres_data']:
                genre.update({'media_id': self.media.id})
                db.session.add(SeriesGenre(**genre))
        elif self.list_type == ListType.ANIME:
            if len(self.media_details['anime_genres_data']) > 0:
                for genre in self.media_details['anime_genres_data']:
                    genre.update({'media_id': self.media.id})
                    db.session.add(AnimeGenre(**genre))
            else:
                for genre in self.media_details['genres_data']:
                    genre.update({'media_id': self.media.id})
                    db.session.add(AnimeGenre(**genre))
        elif self.list_type == ListType.MOVIES:
            for genre in self.media_details['genres_data']:
                genre.update({'media_id': self.media.id})
                db.session.add(MoviesGenre(**genre))

    def add_actors_to_db(self):
        for actor in self.media_details['actors_data']:
            actor.update({'media_id': self.media.id})
            if self.list_type == ListType.SERIES:
                db.session.add(SeriesActors(**actor))
            elif self.list_type == ListType.ANIME:
                db.session.add(AnimeActors(**actor))
            elif self.list_type == ListType.MOVIES:
                db.session.add(MoviesActors(**actor))

    def add_networks_to_db(self):
        for network in self.media_details['networks_data']:
            network.update({'media_id': self.media.id})
            if self.list_type == ListType.SERIES:
                db.session.add(SeriesNetwork(**network))
            elif self.list_type == ListType.ANIME:
                db.session.add(AnimeNetwork(**network))

    def add_seasons_to_db(self):
        for season in self.media_details['seasons_data']:
            season.update({'media_id': self.media.id})
            if self.list_type == ListType.SERIES:
                db.session.add(SeriesEpisodesPerSeason(**season))
            elif self.list_type == ListType.ANIME:
                db.session.add(AnimeEpisodesPerSeason(**season))

    def add_tv_to_db(self):
        if self.list_type == ListType.SERIES:
            self.media = Series(**self.media_details['tv_data'])
        elif self.list_type == ListType.ANIME:
            self.media = Anime(**self.media_details['tv_data'])
        db.session.add(self.media)
        db.session.commit()

        self.add_genres_to_db()
        self.add_actors_to_db()
        self.add_networks_to_db()
        self.add_seasons_to_db()

    def add_movies_to_db(self):
        self.media = Movies(**self.media_details['movies_data'])
        db.session.add(self.media)
        db.session.commit()

        self.add_genres_to_db()
        self.add_actors_to_db()

    def add_media_to_db(self):
        if self.list_type == ListType.SERIES or self.list_type == ListType.ANIME:
            self.add_tv_to_db()
        elif self.list_type == ListType.MOVIES:
            self.add_movies_to_db()

        return self.media
