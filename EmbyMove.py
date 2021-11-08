#!/usr/bin/env python3
import os
import re
import pathlib

EmbyLibrary = './EmbyLibrary'
ConvertDir = './convert'

CATEGORY = {
    'Movie': {
        '1': 'Movies',
        '2': 'Animation Movies',
    },
    'Series': {
        '1': 'TV',
        '2': 'Animation Series',
    }
}
CATEGORY_INPUT = 0
TEST_MODE = True
listOfWords = '66CH|2160p|HDR|imax|10bit|BluRay|6CH|x265|HEVC-PSA|1080p|WEBRip|8CH|2CH|720p|web-dl|remastered|REAL|REPACK|BrRip'
listOfWords = listOfWords.split('|')


def is_linux():
    """
    is_linux()
    Returns True if running on Linux, False otherwise
    """
    return os.name == 'posix'


def set_folder_user_group(folder, user, group):
    """
    set_folder_user_group(folder, user, group)
    Sets the group of the folder
    """
    if is_linux():
        os.system(f'chown -R {user}:{group} {folder}')


def get_dirs(path):
    """
    get_dirs(path)
    Returns a list of all directories in the path
    """
    dirs = [path]
    for i in os.listdir(path):
        if os.path.isdir(os.path.join(path, i)):
            dirs.extend(get_dirs(os.path.join(path, i)))
    return dirs


def combine_path_from_category(category):
    """
    combine_path_from_category(category)
    Combines the path from the category
    """
    path = []
    for value in CATEGORY[category].values():
        path += get_dirs(os.path.join(EmbyLibrary, value))
    return path


def get_media_files_in_dir(path):
    """
    get_media_files_in_dir(path)
    Returns a list of all media files in the path
    """
    media_files = []
    for i in os.listdir(path):
        if os.path.isfile(os.path.join(path, i)):
            if i.endswith('.mkv') or i.endswith('.mp4') or i.endswith('.txt'):
                media_files.append(i)
    return media_files


def remove_word_from_list(list):
    """
    remove_word_from_list(list, words)
    Removes all elements from list containing the word
    """
    temp = []
    for i in range(len(list)):
        if 'Season' not in list[i]:
            if ord(list[i][-1]) < ord('A') or ord(list[i][-1]) > ord('Z'):
                if ord(list[i][-1]) != ord('#'):
                    temp.append(list[i])
    return temp


def find_season(file):
    """
    find_season(file)
    Returns the season number as a string
    """
    for i in range(len(file)):
        if file[i] == 'S':
            if file[i+1].isdigit():
                season = file[i+1]
                if file[i+2].isdigit():
                    season += file[i+2]
                    return season
                else:
                    return season
    return '-1'


def find_episode(file):
    """
    find_episode(file)
    Returns the episode number as a string
    """
    for i in range(len(file)):
        if file[i] == 'E':
            if file[i+1].isdigit():
                episode = file[i+1]
                if file[i+2].isdigit():
                    episode += file[i+2]
                    return episode
                else:
                    return episode
    return '-1'


def find_title(file):
    """
    find_title(file)
    Returns the title as a string
    """
    return file[file.index(f'E{find_episode(file)}')+4:]


def remove_words(file, words):
    """
    remove_words(file, words)
    Removes words from file name
    """
    for word in words:
        file = re.sub(word, '', file, flags=re.I)
    return file


def remove_dot(file):
    """
    remove_dot(file)
    Removes the dot from the file name
    """
    temp = os.path.splitext(file)
    file = re.sub('\.', ' ', temp[0])
    file = file.strip()
    return file + temp[1]


def find_movie_name(file):
    """
    find_movie_name_in_season(file)
    Returns the movie name as a string
    """
    for i in range(len(file)):
        if file[i] == 'S':
            if file[i+1].isdigit():
                movie = file[:i]
                movie = movie.strip()
                return movie
    return file[:file.index(find_year(file))-1]


def find_year(file):
    """
    find_year(file)
    Returns the year as a string
    """
    for i in range(len(file)):
        if file[i].isdigit():
            if file[i+1].isdigit():
                if file[i+2].isdigit():
                    if file[i+3].isdigit():
                        year = file[i:i+4]
                        return year
    return '-1'


def movie_path_in_list(file, combine_path) -> str:
    """
    movie_path_in_list(file)
    Returns path if movie in th list, '' otherwise
    """
    global CATEGORY_INPUT
    file = remove_words(file, listOfWords)
    file = remove_dot(file)

    if find_season(file) != '-1':
        category_str = 'Series'
    else:
        category_str = 'Movie'

    for i in range(len(combine_path)):
        if find_movie_name(file) in combine_path[i]:
            value = os.path.normpath(combine_path[i]).split(os.path.sep)[1]
            CATEGORY_INPUT = get_key(value, CATEGORY[category_str])
            return combine_path[i]
    return ''


# get key from value
def get_key(value, dict):
    for key, val in dict.items():
        if val == value:
            return key
    return '-1'


def create_folder_movie(file):
    """
    create_folder_movie(file)
    Creates a folder for the movie
    """
    global CATEGORY_INPUT
    file = remove_words(file, listOfWords)
    file = remove_dot(file)

    temp = 'Create folder for {' + file + '}?\n'
    category_str = ''
    if find_season(file) != '-1':
        category_str = 'Series'
        for key, value in CATEGORY['Series'].items():
            temp += f"{key}. {value}\n"
    else:
        category_str = 'Movie'
        for key, value in CATEGORY['Movie'].items():
            temp += f"{key}. {value}\n"

    CATEGORY_INPUT = input(temp)
    create_folder_helper(category_str, file)


def create_folder_helper(category_str, file):
    """
    create_folder_helper(category_str, category, file)
    Function helper for create_folder_movie
    """
    alphabet_path = os.path.join(
        EmbyLibrary, CATEGORY[category_str][CATEGORY_INPUT], file[0])
    if not os.path.exists(alphabet_path):
        if TEST_MODE:
            print(f'Create folder {alphabet_path}')
        else:
            os.makedirs(alphabet_path)

    name_path = os.path.join(alphabet_path, find_movie_name(file))
    if not os.path.exists(name_path):
        if TEST_MODE:
            print(f'Create folder {name_path}')
        else:
            os.makedirs(name_path)

    if find_season(file) != '-1':
        season_path = os.path.join(
            name_path, 'Season ' + str(int(find_season(file))))
        if not os.path.exists(season_path):
            if TEST_MODE:
                print(f'Create folder {season_path}')
            else:
                os.makedirs(season_path)


def move_file_into_folder(file):
    """
    move_file_into_folder(file)
    Moves the file into the folder
    """
    if find_season(file) != '-1':
        category_str = 'Series'
    else:
        category_str = 'Movie'

    file = remove_words(file, listOfWords)
    file = remove_dot(file)

    alphabet_path = os.path.join(
        EmbyLibrary, CATEGORY[category_str][CATEGORY_INPUT], file[0])
    name_path = os.path.join(alphabet_path, find_movie_name(file))
    if find_season(file) != '-1':
        season_path = os.path.join(
            name_path, 'Season ' + str(int(find_season(file))))
        # move file to season folder if file not in season folder
        if not os.path.exists(os.path.join(season_path, file)):
            if TEST_MODE:
                print(f'{file} moved to {season_path}')
            else:
                os.rename(file, os.path.join(season_path, file))
    else:
        # move file to movie folder if file not in movie folder
        if not os.path.exists(os.path.join(name_path, file)):
            if TEST_MODE:
                print(f'{file} moved to {name_path}')
            else:
                os.rename(file, os.path.join(name_path, file))


def main():
    media_files = get_media_files_in_dir(ConvertDir)
    set_folder_user_group(ConvertDir, 'emby', 'dietpi')
    for file in media_files:
        if find_season(file) != '-1':
            isMovieExist = movie_path_in_list(
                file, combine_path_from_category('Series'))
            if isMovieExist == '':
                create_folder_movie(file)
        else:
            isMovieExist = movie_path_in_list(
                file, combine_path_from_category('Movie'))
            if isMovieExist == '':
                create_folder_movie(file)

        move_file_into_folder(file)


if __name__ == "__main__":
    main()
    print('Done')