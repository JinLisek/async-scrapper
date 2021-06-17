import argparse


def parse_args():
    parser = argparse.ArgumentParser("Download images from google images")
    parser.add_argument(
        "topics", type=str, nargs="+", help="Text to look for in google images"
    )

    return parser.parse_args()
