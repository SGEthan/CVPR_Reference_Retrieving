from utils import *


# GUI with Gooey
@Gooey(program_name="Reference Downloader")
def main():
    parser = GooeyParser(description="Choose a pdf file to retrieve its references")
    parser.add_argument('File_Path', metavar='File Path', widget="FileChooser")
    args = parser.parse_args()
    input_pdf_file = read_pdf(args.File_Path)  # main progress
    print('done!', flush=True)


if __name__ == '__main__':
    main()
