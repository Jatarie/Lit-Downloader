import re
import sys
import os
import requests
import bs4 as bs

with open('secrets.txt', "r") as f:
    url = f.readline().replace('\n', '')
    other_url = f.readline()


def get_list_of_stories():
    r = requests.get(other_url)
    stories = list(set(re.findall(r'(?<=/s/).+?(?=")', r.text)))
    story_names = []
    for story in stories:
        if "-ch" in story:
            tmp = re.findall(r'.+?(?=-ch)', story)[0]
            story_names.append(tmp)
        else:
            story_names.append(story)
    return sorted(story_names), r


def get_story_author_dict(stories, r):
    story_author_dict = {}
    for story in stories:
        tmp = re.findall(r'{}.+?{}stories/memberpage.php\?uid=[0-9]+(?=")'.format(story, url), r.text)[0] + "&page=submissions"
        author = re.findall(r'http.+?submissions', tmp)[0]
        story_author_dict[story] = author
    return story_author_dict


def get_list_of_story_entries(story, author):
    r = requests.get(author)
    parts = sorted(set(re.findall(r'/s/{}.+?>'.format(story), r.text)))
    parts = [part[:-2] for part in parts]
    return parts


def download_story(story, author, story_parts):
    for part_num, part in enumerate(story_parts):
        sys.stdout.write("\r{}/{}".format(part_num, len(story_parts)))
        with open('files\\{}.txt'.format(story), "a", encoding='utf-8') as f:
            if part_num > 0:
                f.write("\n\n\nPart: {}\n\n\n".format(part_num+1))
            else:
                f.write("Part: 1\n\n\n")
            r = requests.get(url + part[1:])
            page_nums = list(set(re.findall(r'(?<=>)[0-9]+(?=<)', r.text)))
            num_of_pages = max([int(num) for num in page_nums])
            for page in range(1, num_of_pages+1):
                r = requests.get("{}?page={}".format(url + part[1:], page))
                soup = bs.BeautifulSoup(r.text, 'lxml')
                [s.extract() for s in soup(['br'])]
                story_text = soup.find('p').contents
                for line in story_text:
                    if "\n" in line:
                        try:
                            f.write(str(line))
                        except TypeError as e:
                            print(e, str(line))
                            sys.exit()
                    else:
                        f.write(str(line) + "\n")


def main():
    stories, r = get_list_of_stories()
    story_author_dict = get_story_author_dict(stories, r)
    for story, author in story_author_dict.items():
        print("\n\n" + story)
        story_parts = get_list_of_story_entries(story, author)
        download_story(story, author, story_parts)


main()