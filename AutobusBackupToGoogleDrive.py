#!/usr/bin/env python3
import requests
import datetime
import subprocess

API = "https://www.autobus.io/api/snapshots/latest"
TOKEN = ""


def convert_binary_to_string(binary):
    """
    Convert binary to string
    """
    return binary.decode('utf-8')


def rest_get_api(url, params):
    """
    Get API
    """
    try:
        response = requests.get(url, params=params)
        if response.status_code == 200:
            return convert_binary_to_string(response.content)
        else:
            return None
    except requests.exceptions.RequestException as e:
        print(e)
        return None


def download_file(url, file_name):
    """
    Download file
    """
    try:
        response = requests.get(url, stream=True)
        if response.status_code == 200:
            with open(file_name, 'wb') as f:
                for chunk in response.iter_content(chunk_size=1024):
                    if chunk:
                        f.write(chunk)
            return True
        else:
            return False
    except requests.exceptions.RequestException as e:
        print(e)
        return False


def set_file_name_todays_datetime(name):
    """
    Set file name todays date and time
    """
    return name + '_' + datetime.datetime.now().strftime('%Y-%m-%d_%H-%M-%S') + '.sql.gz'


def run_rclone_script(file_name):
    """
    Run rclone script
    """
    return subprocess.call(['rclone', 'copy', file_name, 'google_remote:'])


def check_linux_binary_exists(binary):
    """
    Check if linux binary exists
    """
    try:
        subprocess.call(binary, stdout=subprocess.DEVNULL,
                        stderr=subprocess.DEVNULL)
        return True
    except OSError:
        return False


def main():
    """
    Main
    """
    file_name = set_file_name_todays_datetime('private-vault')
    params = {'token': TOKEN}
    response = rest_get_api(API, params)
    if response:
        download_file(response, file_name)
        if check_linux_binary_exists('rclone'):
            run_rclone_script(file_name)
        else:
            print('rclone binary not found')


if __name__ == '__main__':
    main()
