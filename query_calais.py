import sys
import requests
import os
from functools import partial


calais_url = 'https://api.thomsonreuters.com/permid/calais'


def main():
    try:
        if len(sys.argv) < 4:
            print('3 params are required: 1.input file full path, 2.output directory and 3.access token')
            sys.exit(-1)
        else:
            input_file = sys.argv[1]
            output_dir = sys.argv[2]
            access_token = sys.argv[3]

            if not os.path.exists(input_file):
                print('The file [%s] does not exist' % input_file)
                return
            if not os.path.exists(output_dir):
                os.makedirs(output_dir)

        headers = {'X-AG-Access-Token': access_token, 'Content-Type': 'text/raw', 'outputformat': 'application/json'}
        send_files(input_file, headers, output_dir)
    except Exception as e:
        print('Error in connect ', e)


def send_files(files, headers, output_dir):
    is_file = os.path.isfile(files)
    if is_file:
        send_file(files, headers, output_dir)
    else:
        for file_name in os.listdir(files):
            if os.path.isfile(file_name):
                send_file(file_name, headers, output_dir)
            else:
                send_files(file_name, headers, output_dir)


def send_file(file_name, headers, output_dir):
    if os.path.getsize(file_name) > 90000:
        with open(file_name, 'rb') as f:
            records = iter(partial(f.read, 90000), b'')
            index = 0
            for r in records:
                index += 1
                fn = file_name + '_' + str(index)
                with open(fn, 'wb') as tmp:
                    tmp.write(r)
                tmp.close()
                send_file(fn, headers, output_dir)
    else:
        files = {'file': open(file_name, 'rb')}
        response = requests.post(calais_url, files=files, headers=headers, timeout=80)
        print('status code: %s' % response.status_code)
        content = response.text
        print('Results received: %s' % content)
        if response.status_code == 200:
            save_file(file_name, output_dir, content)


def save_file(file_name, output_dir, content):
    output_file_name = os.path.basename(file_name) + '.json'
    output_file = open(os.path.join(output_dir, output_file_name), 'wb')
    output_file.write(content.encode('utf-8'))
    output_file.close()


if __name__ == "__main__":
    main()
