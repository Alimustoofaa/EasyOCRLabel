# coding:utf8
import os
import csv
import json
import shutil
import random
import argparse


# 删除划分的训练集、验证集、测试集文件夹，重新创建一个空的文件夹
def isCreateOrDeleteFolder(path, flag):
    flagPath = os.path.join(path, flag)

    if os.path.exists(flagPath):
        shutil.rmtree(flagPath)

    os.makedirs(flagPath)
    flagAbsPath = os.path.abspath(flagPath)
    return flagAbsPath


def splitTrainVal(root, absTrainRootPath, absValRootPath, absTestRootPath, trainTxt, valTxt, testTxt, flag):
    # 按照指定的比例划分训练集、验证集、测试集
    dataAbsPath = os.path.abspath(root)

    if flag == "det":
        labelFilePath = os.path.join(dataAbsPath, args.detLabelFileName)
    elif flag == "rec":
        labelFilePath = os.path.join(dataAbsPath, args.recLabelFileName)

    labelFileRead = open(labelFilePath, "r", encoding="UTF-8")
    labelFileContent = labelFileRead.readlines()
    random.shuffle(labelFileContent)
    labelRecordLen = len(labelFileContent)

    for index, labelRecordInfo in enumerate(labelFileContent):
        imageRelativePath = labelRecordInfo.split('\t')[0]
        imageLabel = labelRecordInfo.split('\t')[1]
        imageName = os.path.basename(imageRelativePath)

        if flag == "det":
            imagePath = os.path.join(dataAbsPath, imageName)
        elif flag == "rec":
            imagePath = os.path.join(dataAbsPath, "{}/{}".format(args.recImageDirName, imageName))

        # 按预设的比例划分训练集、验证集、测试集
        trainValTestRatio = args.trainValTestRatio.split(":")
        trainRatio = eval(trainValTestRatio[0]) / 10
        valRatio = trainRatio + eval(trainValTestRatio[1]) / 10
        curRatio = index / labelRecordLen

        if curRatio < trainRatio:
            imageCopyPath = os.path.join(absTrainRootPath, imageName)
            shutil.copy(imagePath, imageCopyPath)
            if flag=='rec':
                newCopyPath = imageCopyPath.split('/')[-1]
                trainTxt.writerow([newCopyPath, imageLabel.replace('\n', '')])
            else:
                imageLabelList = json.loads(imageLabel)
                detPath = os.path.join((absTrainRootPath+'_gt'), ('gt_'+imageName.replace('.jpg', '.txt')))
                removeFile(detPath)
                detTxt = open(detPath, "a", encoding="UTF-8")
                for label in imageLabelList:
                    point_list = sum(label['points'], [])
                    before_idx = len(point_list)
                    point_list.insert(before_idx, label['transcription'])
                    txt = ",".join([str(i) for i in point_list])
                    detTxt.write(txt)
                    detTxt.write('\n')
        elif curRatio >= trainRatio and curRatio < valRatio:
            imageCopyPath = os.path.join(absValRootPath, imageName)
            shutil.copy(imagePath, imageCopyPath)
            if flag=='rec':
                newCopyPath = imageCopyPath.split('/')[-1]
                valTxt.writerow([newCopyPath, imageLabel.replace('\n', '')])
            else:
                imageLabelList = json.loads(imageLabel)
                detPath = os.path.join((absValRootPath+'_gt'), ('gt_'+imageName.replace('.jpg', '.txt')))
                removeFile(detPath)
                detTxt = open(detPath, "a", encoding="UTF-8")
                for label in imageLabelList:
                    point_list = sum(label['points'], [])
                    before_idx = len(point_list)
                    point_list.insert(before_idx, label['transcription'])
                    txt = ",".join([str(i) for i in point_list])
                    detTxt.write(txt)
                    detTxt.write('\n')
        else:
            imageCopyPath = os.path.join(absTestRootPath, imageName)
            shutil.copy(imagePath, imageCopyPath)
            if flag=='rec':
                newCopyPath = imageCopyPath.split('/')[-1]
                testTxt.writerow([newCopyPath, imageLabel.replace('\n', '')])
            else:
                imageLabelList = json.loads(imageLabel)
                detPath = os.path.join((absTestRootPath+'_gt'), ('gt_'+imageName.replace('.jpg', '.txt')))
                removeFile(detPath)
                detTxt = open(detPath, "a", encoding="UTF-8")
                for label in imageLabelList:
                    point_list = sum(label['points'], [])
                    before_idx = len(point_list)
                    point_list.insert(before_idx, label['transcription'])
                    txt = ",".join([str(i) for i in point_list])
                    detTxt.write(txt)
                    detTxt.write('\n')


# 删掉存在的文件
def removeFile(path):
    if os.path.exists(path):
        os.remove(path)


def genDetRecTrainVal(args):
    detAbsTrainRootPath = isCreateOrDeleteFolder(args.detRootPath, "train")
    detAbsTrainRootPathGt = isCreateOrDeleteFolder(args.detRootPath, "train_gt")
    detAbsValRootPath = isCreateOrDeleteFolder(args.detRootPath, "val")
    detAbsValRootPathGt = isCreateOrDeleteFolder(args.detRootPath, "val_gt")
    detAbsTestRootPath = isCreateOrDeleteFolder(args.detRootPath, "test")
    detAbsTestRootPathGt = isCreateOrDeleteFolder(args.detRootPath, "test_gt")
    recAbsTrainRootPath = isCreateOrDeleteFolder(args.recRootPath, "train")
    recAbsValRootPath = isCreateOrDeleteFolder(args.recRootPath, "val")
    recAbsTestRootPath = isCreateOrDeleteFolder(args.recRootPath, "test")

    removeFile(os.path.join(args.recRootPath, "train.csv"))
    removeFile(os.path.join(args.recRootPath, "val.csv"))
    removeFile(os.path.join(args.recRootPath, "test.csv"))

    recTrainCsv = open(os.path.join(args.recRootPath+'/train', "labels.csv"), "a", encoding="UTF-8", newline='')
    recValCsv= open(os.path.join(args.recRootPath+'/val', "labels.csv"), "a", encoding="UTF-8", newline='')
    recTestCsv = open(os.path.join(args.recRootPath+'/test', "labels.csv"), "a", encoding="UTF-8", newline='')


    header = ['filename', 'words']
    recTrainTxt = csv.writer(recTrainCsv)
    recTrainTxt.writerow(header)

    recValTxt = csv.writer(recValCsv)
    recValTxt.writerow(header)

    recTestTxt = csv.writer(recTestCsv)
    recTestTxt.writerow(header)

    splitTrainVal(args.datasetRootPath, detAbsTrainRootPath, detAbsValRootPath, detAbsTestRootPath, 'detTrainTxt', 'detValTxt',
                  'detTestTxt', "det")

    for root, dirs, files in os.walk(args.datasetRootPath):
        for dir in dirs:
            if dir == 'crop_img':
                splitTrainVal(root, recAbsTrainRootPath, recAbsValRootPath, recAbsTestRootPath, recTrainTxt, recValTxt,
                              recTestTxt, "rec")
            else:
                continue
        break



if __name__ == "__main__":
    # Function description: divide the training set, verification set and test set of detection and recognition respectively
    # Description: You can adjust the parameters according to your own path and needs. Image data is often marked by multiple people in batches. Each batch of image data is placed in a folder and marked with EasyOCRLabel.
    # In this way, there will be multiple labeled image folders to summarize and divide the training set, verification set, and test set requirements
    parser = argparse.ArgumentParser()
    parser.add_argument(
        "--trainValTestRatio",
        type=str,
        default="7:0:3",
        help="ratio of trainset:valset:testset")
    parser.add_argument(
        "--datasetRootPath",
        type=str,
        default="train_data/",
        help="path to the dataset marked by ppocrlabel, E.g, dataset folder named 1,2,3..."
    )
    parser.add_argument(
        "--detRootPath",
        type=str,
        default="train_data/det",
        help="the path where the divided detection dataset is placed")
    parser.add_argument(
        "--recRootPath",
        type=str,
        default="train_data/rec",
        help="the path where the divided recognition dataset is placed"
    )
    parser.add_argument(
        "--detLabelFileName",
        type=str,
        default="Label.txt",
        help="the name of the detection annotation file")
    parser.add_argument(
        "--recLabelFileName",
        type=str,
        default="rec_gt.txt",
        help="the name of the recognition annotation file"
    )
    parser.add_argument(
        "--recImageDirName",
        type=str,
        default="crop_img",
        help="the name of the folder where the cropped recognition dataset is located"
    )
    args = parser.parse_args()
    genDetRecTrainVal(args)
