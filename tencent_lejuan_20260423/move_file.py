import logging 
import os 
import shutil

def move_folders_by_suffix (source_dir_name = 'images/cover_images/00'):
    root_path = os.getcwd()
    source_path = os.path.join(root_path, source_dir_name)

    if not os.path.exists(source_path):
        logging.debug(f"not source dir = {source_path}")
        return 
    print(f"scanning {source_path}")

    for folder_name in os.listdir(source_path):
        source_folder_path = os.path.join(source_path, folder_name)
        if os.path.isdir(source_folder_path):
            if len(folder_name)>=2:
                target_folder_name = folder_name[-2:]

            else:
                target_folder_name = f"0{folder_name}"

            target_dir_path = os.path.join(root_path, "images/cover_images/", target_folder_name)

            # move the sub folder'
            if not os.path.exists(target_dir_path):
                os.makedirs(target_dir_path)


            final_dest = os.path.join(target_dir_path, folder_name)
            if os.path.exists(final_dest):
                print(f"{final_dest} has already exists.")
            else:
                shutil.move(source_folder_path, final_dest)

if __name__ == "__main__":
    move_folders_by_suffix()

    