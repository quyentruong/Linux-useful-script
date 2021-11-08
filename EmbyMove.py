#!/usr/bin/env python3
import os
import re
import sys

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
listOfWords = '66CH|2160p|HDR|imax|10bit|BluRay|6CH|x265|HEVC-PSA|1080p|WEBRip|8CH|2CH|720p|web-dl|remastered|REAL|REPACK|BrRip'
listOfWords = listOfWords.split('|')


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


SeriesDirs = remove_word_from_list(combine_path_from_category('Movie'))
# print('Movies: ' + '\n'.join(SeriesDirs))


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
    file = re.sub('\.', ' ', file)
    file = file.strip()
    return file


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


test_movie = "DC's.Legends.of.Tomorrow.S07E04.Speakeasy.Does.It.1080p.WEBRip.6CH.x265.HEVC-PSA"
test_movie2 = 'ZThe.Hitmans.Wifes.Bodyguard.2021.EXTENDED.720p.WEBRip.2CH.x265.HEVC-PSA'


def movie_path_in_list(file) -> str:
    """
    movie_path_in_list(file)
    Returns path if movie in th list, '' otherwise
    """
    file = remove_words(file, listOfWords)
    file = remove_dot(file)

    for i in range(len(SeriesDirs)):
        if find_movie_name(file) in SeriesDirs[i]:
            return SeriesDirs[i]
    return ''


def create_folder_movie(file):
    """
    create_folder_movie(file)
    Creates a folder for the movie
    """
    file = remove_words(file, listOfWords)
    file = remove_dot(file)

    temp = 'Create folder for {' + file + '}?\n'
    if find_season(file) != '-1':
        for key, value in CATEGORY['Series'].items():
            temp += f"{key}. {value}\n"
    else:
        for key, value in CATEGORY['Movie'].items():
            temp += f"{key}. {value}\n"

    category = input(temp)
    for key in CATEGORY.keys():
        create_folder_helper(key, category, file)


def create_folder_helper(category_str, category, file):
    """
    create_folder_helper(category_str, category, file)
    Function helper for create_folder_movie
    """
    alphabet_path = os.path.join(
        EmbyLibrary, CATEGORY[category_str][category], file[0])
    if not os.path.exists(alphabet_path):
        os.makedirs(alphabet_path)
    name_path = os.path.join(alphabet_path, find_movie_name(file))
    if not os.path.exists(name_path):
        os.makedirs(name_path)
    if find_season(file) != '-1':
        season_path = os.path.join(
            name_path, 'Season ' + int(find_season(file)))
        if not os.path.exists(season_path):
            os.makedirs(season_path)


test_movie2 = remove_words(test_movie2, listOfWords)
test_movie2 = remove_dot(test_movie2)


# print(find_movie_name(test_movie2))
# print(find_title(test_movie2))

# print(f'{find_movie_name(test_movie2)} S{find_season(test_movie2)}E{find_episode(test_movie2)} {find_title(test_movie2)}')
# create_folder_movie(test_movie2)
# print(test_movie)
# print(int (find_season(test_movie)))
# print(SeriesDirs)
# print(find_movie_name_in_season(test_movie) in SeriesDirs)
