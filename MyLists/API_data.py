

class API_data():
    def autocomplete_search(self, element_name, list_type):
        try:
            if list_type != ListType.MOVIES:
                response = requests.get("https://api.themoviedb.org/3/search/tv?api_key={0}&query={1}"
                                        .format(themoviedb_api_key, element_name))
            if list_type == ListType.MOVIES:
                response = requests.get("https://api.themoviedb.org/3/search/movie?api_key={0}&query={1}"
                                        .format(themoviedb_api_key, element_name))
        except:
            return [{"nb_results": 0}]

        if response.status_code == 401:
            app.logger.error('[SYSTEM] Error requesting themoviedb API : invalid API key')
            return [{"nb_results": 0}]

        data = json.loads(response.text)

        if data.get("total_results", 0) == 0:
            return [{"nb_results": 0}]

        if list_type == ListType.SERIES:
            # Take only the first 6 results for the autocomplete
            # If there is an anime in the 6 results, loop until the next one
            # There are 20 results per page
            tmdb_results = []
            i = 0
            while i < data["total_results"] and i < 20 and len(tmdb_results) < 6:
                # genre_ids : list
                if "genre_ids" in data["results"][i]:
                    genre_ids = data["results"][i]["genre_ids"]
                else:
                    genre_ids = ["Unknown"]

                # origin_country : list
                if "origin_country" in data["results"][i]:
                    origin_country = data["results"][i]["origin_country"]
                else:
                    origin_country = ["Unknown"]

                # original_language : string
                if "original_language" in data["results"][i]:
                    original_language = data["results"][i]["original_language"]
                else:
                    original_language = "Unknown"

                # To not add anime in the series table, we need to check if it's an anime and if it comes from Japan
                if (16 in genre_ids and "JP" in origin_country) or (16 in genre_ids and original_language == "ja"):
                    i = i + 1
                    continue

                series_data = {"tmdb_id": data["results"][i]["id"],
                               "name": data["results"][i]["name"]}

                if data["results"][i]["poster_path"] is not None:
                    series_data["poster_path"] = "{0}{1}".format("http://image.tmdb.org/t/p/w300",
                                                                 data["results"][i]["poster_path"])
                else:
                    series_data["poster_path"] = url_for('static', filename="covers/series_covers/default.jpg")

                if "first_air_date" in data["results"][i] and data["results"][i]["first_air_date"].split('-') != ['']:
                    series_data["first_air_date"] = data["results"][i]["first_air_date"].split('-')[0]
                else:
                    series_data["first_air_date"] = "Unknown"

                tmdb_results.append(series_data)
                i = i + 1
        elif list_type == ListType.ANIME:
            # Take only the first 6 results for the autocomplete
            # If there is a series in the 6 results, loop until the next one
            # There are 20 results per page
            tmdb_results = []
            i = 0
            while i < data["total_results"] and i < 20 and len(tmdb_results) < 6:
                # genre_ids : list
                if "genre_ids" in data["results"][i]:
                    genre_ids = data["results"][i]["genre_ids"]
                else:
                    genre_ids = ["Unknown"]

                # origin_country : list
                if "origin_country" in data["results"][i]:
                    origin_country = data["results"][i]["origin_country"]
                else:
                    origin_country = ["Unknown"]

                # original_language : string
                if "original_language" in data["results"][i]:
                    original_language = data["results"][i]["original_language"]
                else:
                    original_language = "Unknown"

                # To add only anime in the anime table, we need to check if it's an anime and it comes from Japan
                if (16 in genre_ids and "JP" in origin_country) or (16 in genre_ids and original_language == "ja"):
                    anime_data = {
                        "tmdb_id": data["results"][i]["id"],
                        "name": data["results"][i]["name"]
                    }

                    if data["results"][i]["poster_path"] is not None:
                        anime_data["poster_path"] = "{}{}" \
                            .format("http://image.tmdb.org/t/p/w300", data["results"][i]["poster_path"])
                    else:
                        anime_data["poster_path"] = url_for('static', filename="covers/anime_covers/default.jpg")

                    if data["results"][i]["first_air_date"].split('-') != ['']:
                        anime_data["first_air_date"] = data["results"][i]["first_air_date"].split('-')[0]
                    else:
                        anime_data["first_air_date"] = "Unknown"

                    tmdb_results.append(anime_data)
                i = i + 1
        elif list_type == ListType.MOVIES:
            try:
                response = requests.get("https://api.themoviedb.org/3/search/movie?api_key={0}&query={1}"
                                        .format(themoviedb_api_key, element_name))
            except:
                return [{"nb_results": 0}]

            if response.status_code == 401:
                app.logger.error('[SYSTEM] Error requesting themoviedb API : invalid API key')
                return [{"nb_results": 0}]

            data = json.loads(response.text)
            try:
                if data["total_results"] == 0:
                    return [{"nb_results": 0}]
            except:
                return [{"nb_results": 0}]

            # Take only the first 6 results for the autocomplete. There are 20 results per page
            tmdb_results = []
            i = 0
            while i < data["total_results"] and i < 20 and len(tmdb_results) < 6:
                movies_data = {"tmdb_id": data["results"][i]["id"],
                               "name": data["results"][i]["title"]}

                if data["results"][i]["poster_path"] is not None:
                    movies_data["poster_path"] = "{0}{1}" \
                        .format("http://image.tmdb.org/t/p/w300", data["results"][i]["poster_path"])
                else:
                    movies_data["poster_path"] = url_for('static', filename="covers/movies_covers/default.jpg")

                if "release_date" in data["results"][i] != ['']:
                    movies_data["first_air_date"] = data["results"][i]["release_date"].split('-')[0]
                else:
                    movies_data["first_air_date"] = "Unknown"

                tmdb_results.append(movies_data)
                i = i + 1

        return tmdb_results

    def add_element_from_api(self, element_id, list_type, element_cat):
        element_data = get_element_data_from_api(element_id, list_type)
        element_actors = get_element_actors_from_api(element_id, list_type)

        if element_data is None:
            return flash("There was a problem while getting the info from the API."
                         " Please try again later.", "warning")

        try:
            element_cover_path = element_data["poster_path"]
        except:
            element_cover_path = None

        element_cover_id = save_api_cover(element_cover_path, list_type)

        if element_cover_id is None:
            element_cover_id = "default.jpg"
            flash("There was a problem while getting the poster from the API."
                  " Please try to refresh later.", "warning")

        element_id = add_element_in_base(element_data, element_actors, element_cover_id, list_type)
        add_element_to_user(element_id, int(current_user.id), list_type, element_cat)

    def get_element_data_from_api(self, api_id, list_type):
        try:
            if list_type != ListType.MOVIES:
                response = requests.get("https://api.themoviedb.org/3/tv/{0}?api_key={1}"
                                        .format(api_id, themoviedb_api_key))
            if list_type == ListType.MOVIES:
                response = requests.get("https://api.themoviedb.org/3/movie/{0}?api_key={1}"
                                        .format(api_id, themoviedb_api_key))
        except:
            return None

        if response.status_code == 401:
            app.logger.error('[SYSTEM] Error requesting themoviedb API : invalid API key')
            return None

        return json.loads(response.text)

    def get_element_actors_from_api(self, api_id, list_type):
        if list_type != ListType.MOVIES:
            try:
                response = requests.get("https://api.themoviedb.org/3/tv/{0}/credits?api_key={1}"
                                        .format(api_id, themoviedb_api_key))
            except:
                return None
            if response.status_code == 401:
                app.logger.error('[SYSTEM] Error requesting themoviedb API : invalid API key')
                return None

        elif list_type == ListType.MOVIES:
            try:
                response = requests.get("https://api.themoviedb.org/3/movie/{0}/credits?api_key={1}"
                                        .format(api_id, themoviedb_api_key))
            except:
                return None
            if response.status_code == 401:
                app.logger.error('[SYSTEM] Error requesting themoviedb API : invalid API key')
                return None

        else:
            return None

        return json.loads(response.text)

    def save_api_cover(self, element_cover_path, list_type):
        if element_cover_path is None:
            return "default.jpg"

        element_cover_id = "{}.jpg".format(secrets.token_hex(8))

        if list_type == ListType.SERIES:
            if platform.system() == "Windows":
                local_covers_path = os.path.join(app.root_path, "static\\covers\\series_covers\\")
            else:  # Linux & macOS
                local_covers_path = os.path.join(app.root_path, "static/covers/series_covers/")
        elif list_type == ListType.ANIME:
            if platform.system() == "Windows":
                local_covers_path = os.path.join(app.root_path, "static\\covers\\anime_covers\\")
            else:  # Linux & macOS
                local_covers_path = os.path.join(app.root_path, "static/covers/anime_covers/")
        elif list_type == ListType.MOVIES:
            if platform.system() == "Windows":
                local_covers_path = os.path.join(app.root_path, "static\\covers\\movies_covers\\")
            else:  # Linux & macOS
                local_covers_path = os.path.join(app.root_path, "static/covers/movies_covers/")

        try:
            urllib.request.urlretrieve("http://image.tmdb.org/t/p/w300{}".format(element_cover_path),
                                       "{}{}".format(local_covers_path, element_cover_id))
        except:
            return None

        img = Image.open("{}{}".format(local_covers_path, element_cover_id))
        img = img.resize((300, 450), Image.ANTIALIAS)
        img.save("{0}{1}".format(local_covers_path, element_cover_id), quality=90)

        return element_cover_id
