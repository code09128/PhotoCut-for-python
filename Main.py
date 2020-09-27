import matplotlib.pyplot as plt
import os
import cv2
import shutil

from PIL import Image
from cut_the_Bone import bone_cutting
from ct_exception import CT_Exception
from PredictBoneScan import Predic
# 引入 pathlib 模組
from pathlib import Path

img_source_folder_path = "./images/forTest" #來源資料夾
output_folder_path = "./test_output" #輸出資料夾
exception_folder_path = "./exception_output" #問題檔案資料夾
old_folder = "./images/OldPhoto"
merge_folder_path = "./images/merge" #圖片和成資料夾
my_folder = Path("./images/merge/predict") #資料夾產生路徑

if __name__ == "__main__":
    from time import time
    startTime = time()
    
    img_names_list = os.listdir(img_source_folder_path)
    for img_name in img_names_list:
        try:
            try:
                bone_img_list = bone_cutting(cv2.imread(img_source_folder_path+"/"+img_name))
            except CT_Exception:
                print("Unknown Pattern Image!!")
                print(img_name,"move to the exception_output folder!!")
                cv2.imwrite(os.path.join(exception_folder_path,img_name),cv2.imread(os.path.join(img_source_folder_path,img_name)))
            except IndexError as e:
                print(img_name,"Image's body not long enough!!")
                cv2.imwrite(os.path.join(exception_folder_path,""+img_name),cv2.imread(os.path.join(img_source_folder_path,img_name)))
            else:
                index = 0
                for bone_img in bone_img_list:
                    cv2.imwrite(output_folder_path+"/"+"".join(img_name.split(".")[:len(img_name.split("."))-1])+"_"+str(index)+".jpg",bone_img)
                    index+=1
            
            #鏡像合併圖片
            img1 = Image.open(output_folder_path+"/"+"".join(img_name.split(".")[:len(img_name.split("."))-1])+"_"+str(0)+".jpg")
            img2 = Image.open(output_folder_path+"/"+"".join(img_name.split(".")[:len(img_name.split("."))-1])+"_"+str(1)+".jpg")
            img3 = Image.new('RGB',(3000,3000),"white")
            img3.paste(img1,(900,600))
            img3.paste(img2,(1500,600))
            img3.save(merge_folder_path+"/"+"".join(img_name.split(".")[:len(img_name.split("."))-1])+".jpg")

            # plt.imshow(img3)
            # plt.show()

            # 檢查路徑是否存在
            if not my_folder.exists():
                os.makedirs(my_folder)
                shutil.move(merge_folder_path + "/" + "".join(img_name.split(".")[:len(img_name.split(".")) - 1]) + ".jpg",my_folder)

            else:
                shutil.move(merge_folder_path + "/" + "".join(img_name.split(".")[:len(img_name.split(".")) - 1]) + ".jpg",my_folder)

            print(img_name, "載入成功", "Cost Time:" + str(time() - startTime))
            print(img_name, "載入成功", "Cost Time:" + str(time() - startTime),file=open(r"D:\Dustin\AI\20200220_BoneScanCut\message_data\okay.txt", "a"), flush=True)

            # 刪除處理好的原圖
            # os.remove(img_source_folder_path + "/" + img_name)

            # 搬移處理原圖
            shutil.move(img_source_folder_path + "/" + img_name, old_folder)

        except:
            os.remove(img_source_folder_path + "/" + img_name)

            print(img_name, "載入失敗", "Cost Time:" + str(time() - startTime))
            print(img_name, "載入失敗", "Cost Time:" + str(time() - startTime),file=open(r"D:\Dustin\AI\20200220_BoneScanCut\message_data\error.txt", "a"), flush=True)

    print("Cost Time:" + str(time() - startTime))

    # 執行預測動作
    # Predic(merge_folder_path)
    # print("done:" + str(time() - startTime))
    # print("done:" + str(time() - startTime),
    # file=open(r"D:\Dustin\AI\20200220_BoneScanCut\message_data\finished.txt", "a"), flush=True)