import torch
import numpy as np
from torch import nn, optim
from gaze_model import annetV2, annetV3
from eye_dataset import eyeDataset
from torchvision import transforms
from torch.utils.data import DataLoader
from torch.utils.data import random_split

def main():
    EPOCHS = 25
    BATCH_SIZE = 64
    WEIGHT_DECAY = 0.0
    LEARNING_RATE = 0.0001
    SAVE = './garage/V3/'
    dataset_dir = './eye_dataset/'
    device = torch.device("cuda:0" if torch.cuda.is_available() else "cpu")

    net = annetV3(device=device, in_channels=2)
    #net.load_state_dict(torch.load('./garage/V3/epoch_125_test0.0029_train0.000541.pth', map_location=device))

    img_transform = transforms.Compose([ # bw transform
            transforms.ColorJitter(brightness=0.3, contrast=0.3),
        ])
    # img_transform = transforms.Compose([ # rgb transform
    #         transforms.ColorJitter(brightness=0.3, contrast=0.3, saturation=0.3, hue=0.15),
    #         transforms.Normalize(mean=[0.485, 0.456, 0.406], std=[0.229, 0.224, 0.225]),
    #     ])
    dataset = eyeDataset(dataset_dir, img_transform, use_left_eye=True, use_right_eye=True, pose=True)
    
    train_split = 0.9
    train_set, test_set = random_split(dataset, [int(len(dataset)*train_split), int(len(dataset)-(int(len(dataset)*train_split)))], generator=torch.Generator().manual_seed(42))
    print("train_set: " + str(len(train_set)))
    print("test_set: " + str(len(test_set)))

    train_loader = DataLoader(train_set, BATCH_SIZE, shuffle=True, num_workers=2, pin_memory=True)
    test_loader = DataLoader(test_set, BATCH_SIZE, shuffle=True, num_workers=2, pin_memory=True)

    optimizer = optim.AdamW(net.parameters(), lr=LEARNING_RATE, weight_decay=WEIGHT_DECAY)
    criterion = nn.MSELoss()

    train_loss = []
    test_loss = []
    all_loss = []
    epoch = 0

    print("start training...", flush=True)

    for epoch in range(EPOCHS):  # loop over the dataset multiple times
        train_loss = []
        test_loss = []
        #train part
        for i, data in enumerate(train_loader, 0):
            # get the inputs; data is a list of [inputs, labels]
            inputs, labels = data
            labels = labels.to(device)

            # zero the parameter gradients
            optimizer.zero_grad()

            # forward + backward + optimize
            outputs = net(inputs)
            loss = criterion(outputs, labels)
            loss.backward()
            optimizer.step()

            train_loss.append(loss.item())

        #test part
        with torch.no_grad():
            for i, data in enumerate(test_loader, 0):
                # get the inputs; data is a list of [inputs, labels]
                inputs, labels = data
                labels = labels.to(device)

                # forward + backward + optimize
                outputs = net(inputs)
                loss = criterion(outputs, labels)

                test_loss.append(loss.item())

        train_loss = np.mean(train_loss)
        test_loss = np.mean(test_loss)
        print(f"Finished epoc:{epoch+126} - train_loss: {train_loss:.7f} test_loss: {test_loss:.7f} diff_loss: {train_loss-test_loss:.7f}")
        
        all_loss.append([train_loss, test_loss])
        
        torch.save(net.state_dict(), SAVE + "epoch_" + str(epoch+126) + "_test" + str(round(test_loss, 6)) + "_train" + str(round(train_loss, 6)) + ".pth")

    print("Finished")

    torch.save(torch.tensor(all_loss), SAVE + "loss.pth")

if __name__ == "__main__":
    main()

# old method
# import torch
# import numpy as np
# from torch import nn, optim
# from gaze_model import annetV3
# from eye_dataset import eyeDataset
# from torchvision import transforms
# from torch.utils.data import DataLoader
# from torch.utils.data import random_split

# def main():
#     EPOCHS = 50
#     BATCH_SIZE = 64
#     WEIGHT_DECAY = 0.03
#     LEARNING_RATE = 0.0001
#     PRINT_EVERY = 1024
#     SAVE = './garage/test'
#     dataset_dir = './eye_dataset/'
#     device = torch.device("cuda:0" if torch.cuda.is_available() else "cpu")

#     net = annetV3(device=device, in_channels=2)
#     #net.load_state_dict(torch.load('./garage/08.pth', map_location=device))

#     img_transform = transforms.Compose([ # bw transform
#             transforms.ColorJitter(brightness=0.3, contrast=0.3),
#         ])
#     # img_transform = transforms.Compose([ # rgb transform
#     #         transforms.ColorJitter(brightness=0.3, contrast=0.3, saturation=0.3, hue=0.15),
#     #         transforms.Normalize(mean=[0.485, 0.456, 0.406], std=[0.229, 0.224, 0.225]),
#     #     ])
#     dataset = eyeDataset(dataset_dir, img_transform, use_left_eye=True, use_right_eye=True, pose=True)
    
#     train_split = 0.9
#     train_set, test_set = random_split(dataset, [int(len(dataset)*train_split), int(len(dataset)-(int(len(dataset)*train_split)))], generator=torch.Generator().manual_seed(42))
#     print("train_set: " + str(len(train_set)))
#     print("test_set: " + str(len(test_set)))

#     train_loader = DataLoader(train_set, BATCH_SIZE, shuffle=True, num_workers=2, pin_memory=True)
#     test_loader = DataLoader(test_set, BATCH_SIZE, shuffle=True, num_workers=2, pin_memory=True)

#     optimizer = optim.AdamW(net.parameters(), lr=LEARNING_RATE, weight_decay=WEIGHT_DECAY)
#     criterion = nn.MSELoss()
#     train_loss = []

#     print("start training...", flush=True)

#     for epoch in range(EPOCHS):  # loop over the dataset multiple times

#         running_loss = 0.0
#         for i, data in enumerate(train_loader, 0):
#             # get the inputs; data is a list of [inputs, labels]
#             inputs, labels = data
#             labels = labels.to(device)

#             # zero the parameter gradients
#             optimizer.zero_grad()

#             # forward + backward + optimize
#             outputs = net(inputs)
#             loss = criterion(outputs, labels)
#             loss.backward()
#             optimizer.step()

#             train_loss.append(loss.item())

#             # print statistics
#             running_loss += loss.item()
#             if i % PRINT_EVERY == 0:    # print every PRINT_EVERY mini-batches
#                 print(f'[{epoch + 1}] loss: {np.mean(train_loss[-PRINT_EVERY:]):.6f}')
#                 running_loss = 0.0

#     #torch.save(net.state_dict(), SAVE + "_epoch_" + str(0+EPOCHS) + "_" + str(round(np.mean(train_loss), 6)) + ".pth")

#     print("Finished Training - loss: {:.4f}".format(np.mean(train_loss)))
#     print("start testing...", flush=True)
#     test_loss = []
    
#     running_loss = 0.0
#     with torch.no_grad():
#         for i, data in enumerate(test_loader, 0):
#             # get the inputs; data is a list of [inputs, labels]
#             inputs, labels = data
#             labels = labels.to(device)

#             # forward + backward + optimize
#             outputs = net(inputs)
#             loss = criterion(outputs, labels)

#             test_loss.append(loss.item())

#             # print statistics
#             running_loss += loss.item()
#             if i % PRINT_EVERY == 0:    # print every PRINT_EVERY mini-batches
#                 print(f'[{epoch + 1}] loss: {np.mean(train_loss[-PRINT_EVERY:]):.6f}')
#                 running_loss = 0.0

#     print("Finished Testing - loss: {:.4f}".format(np.mean(test_loss)))

#     print("Saving modle....")
#     torch.save(net.state_dict(), SAVE + "_epoch_" + str(0+EPOCHS) + "_test" + str(round(np.mean(test_loss), 6)) + "_train" + str(round(np.mean(train_loss), 6)) + ".pth")

# if __name__ == "__main__":
#     main()

# https://pytorch.org/tutorials/beginner/blitz/cifar10_tutorial.html#train-the-network

#TODO make 2 models, one with pose and one without, test both models on multi-view dataset and self produced data