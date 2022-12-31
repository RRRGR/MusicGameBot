import json

from numpy import single


def han2kana(hangle: str) -> str:

    """
    Return the reading of hangle word as hiragana.
    """

    with open("rc/hangle2kana.json") as f:
        han2kana_dic = json.load(f)
    trans_han2kana = str.maketrans(han2kana_dic)
    kana = hangle.translate(trans_han2kana)
    return kana


def en2kana(en: str) -> str:

    vowels = ["a", "i", "u", "e", "o"]
    kana = ""

    with open("rc/en2kana.json") as f:
        en2kana_dic = json.load(f)

    counter = 0
    skip = []
    done_silent_e = False
    for i in range(len(en)):

        if i in skip:
            skip.remove(i)
            counter += 1
            continue

        single_str = en[i]
        if single_str in vowels:
            # vowels単体
            kana += en2kana_dic["normal"][single_str]
        else:
            try:
                if en[i + 1] in vowels and en[i + 2] == "r":
                    # vowels + r (ex. bard)
                    kana += en2kana_dic["r"][single_str + en[i + 1]]
                    skip.append(i + 1)
                    skip.append(i + 2)
                elif (
                    en[i + 1] in vowels
                    and en[i + 2] not in vowels
                    and en[i + 3] == "e"
                    and done_silent_e is False
                ):
                    # silent e (ex. game)
                    kana += en2kana_dic["e"][single_str + en[i + 1]]
                    skip.append(i + 1)
                    skip.append(i + 3)
                    done_silent_e = True
                elif en[i + 1] in vowels:
                    # ローマ字読み (ex. ma)
                    done_silent_e = False
                    if i + 1 not in skip:
                        # 普通
                        kana += en2kana_dic["normal"][single_str + en[i + 1]]
                        skip.append(i + 1)
                    else:
                        # skipするとき(consonant単体)
                        kana += en2kana_dic["normal"][single_str]
                else:
                    # consonant単体
                    done_silent_e = False
                    kana += en2kana_dic["normal"][single_str]
            except IndexError:
                kana += en2kana_dic["normal"][single_str]

        counter += 1

    return kana


def en2rome(en: str) -> str:

    vowels = ["a", "i", "u", "e", "o"]
    rome = ""

    with open("rc/en2rome.json") as f:
        en2rome_dic = json.load(f)

    counter = 0
    skip = []
    done_silent_e = False

    try:
        if en[0] == "k" and en[1] == "n":
            en = en[1:]
        elif en[0] == "g" and en[1] == "n":
            en = en[1:]
        elif en[0] == "p" and en[1] == "s":
            en = en[1:]
        elif en[0] == "p" and en[1] == "t":
            en = en[1:]
        elif en[0] == "w" and en[1] == "r":
            en = en[1:]
        elif en[0] == "w" and en[1] == "h":
            en = "w" + en[2:]

        if en[-2] == "m" and en[-1] == "n":
            en = en[:-1]
        elif en[-2] == "m" and en[-1] == "b":
            en = en[:-1]
        elif en[-2] == "g" and en[-1] == "n":
            en = en[:-2] + "n"
        elif en[-2] == "g" and en[-1] == "m":
            en = en[:-1]
    except IndexError:
        pass

    for i in range(len(en)):
        single_str = en[i]

        if i in skip:
            skip.remove(i)
            counter += 1
            continue

        try:
            if (single_str + en[i + 1] in en2rome_dic["double"]) and (
                i + 1 not in skip
            ):
                # 母音が連続する時とか
                done_silent_e = False
                rome += en2rome_dic["double"][single_str + en[i + 1]]
                skip.append(i + 1)
            elif en[i + 1] in vowels and en[i + 2] == "r":
                # vowels + r (ex. bard)
                done_silent_e = False
                if single_str == "c":
                    single_str = "s"
                rome += single_str + en2rome_dic["r"][en[i + 1]]
                skip.append(i + 1)
                skip.append(i + 2)
            elif (
                en[i + 1] in vowels
                and en[i + 2] not in vowels
                and en[i + 3] == "e"
                and done_silent_e is False
            ):
                # silent e (ex. game)
                rome += single_str + en2rome_dic["e"][en[i + 1]]
                skip.append(i + 1)
                skip.append(i + 3)
                done_silent_e = True

            else:
                done_silent_e = False
                rome += single_str
        except IndexError:
            done_silent_e = False
            rome += single_str

        counter += 1

    return rome


def rome2kana(rome: str) -> str:
    vowels = ["a", "i", "u", "e", "o"]
    kana = ""

    with open("rc/rome2kana.json") as f:
        rome2kana_dic = json.load(f)

    skip = []
    for i in range(len(rome)):

        if i in skip:
            skip.remove(i)
            continue

        single_str = rome[i]

        try:
            if rome[i + 1] in vowels:
                kana += rome2kana_dic[single_str + rome[i + 1]]
                skip.append(i + 1)
            else:
                kana += rome2kana_dic[single_str]
        except IndexError:
            kana += rome2kana_dic[single_str]

    return kana


def kana2en(kana: str) -> str:
    """
    Return the reading of alphabet word as hiragana.
    """
    with open("rc/kana2en.json") as f:
        kana2en_dic = json.load(f)
    trans_kana2en = str.maketrans(kana2en_dic)
    en = kana.translate(trans_kana2en)
    return en
