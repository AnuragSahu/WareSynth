# WareSynth

 A procedural synthetic  data  generation pipeline  that  can  be  used  to  generate  3D  warehouse  scenes and  automate  the  process  of  data  capture  and  generating corresponding  annotation.

## A Sample Warehouse

<img src="./assets/tes.png" alt="Depth and Trajectory Example" > 

## The Generation of Warehouse

Our  generation  process  entails  placement  of  objects  in the scene procedurally in a randomized fashion, followed by adjustment of the lighting and textures. We perform texture editing and manipulate roughness and reflectance properties of objects to mimic real warehouse scenes.We  start  with  an  empty  warehouse.  Racks  are  placed inside the warehouse according to a randomly generated 2D occupancy map. Lighting in the warehouse is also according to the same map, where we illuminate the corridors and also introduce  ambient  lighting.  We  keep  the  inter-shelf  heightand  number  of  shelves  in  racks,  width  of  corridors  and overall  rack  density  of  the  warehouse  as  parameters  which can be tuned as per requirements. It is important to note that WareSynth is  not  constrained  by specific  settings.  The existing models can be readily substituted with custom box and rack models to configure the warehouse.

## Paper

This Synthetic Warehouse Pipeline generation is a part of "RackLay: Multi-Layer Layout Estimation for Warehouse Racks", The Links to paper, code, dataset, are as follows : <br>
Link to Paper :  <a href = "https://arxiv.org/abs/2103.09174" > arXiv </a> <br>
Link to Code for WareSynth : <a href = "https://github.com/AnuragSahu/WareSynth"> WareSynth Code </a><br>
Link to Code for RackLay : <a href = "https://github.com/Avinash2468/RackLay"> RackLay Code </a><br>
Download Dataset : <a href = "https://drive.google.com/drive/folders/1-GizhhfVOeyITYK0nIYpoyQPgtgALHvG?usp=sharing"> Dataset </a>

## Capabilities of WareSynth

The absolute Depth Map and Camera positions and orientations can be obtained, other usefull information like 2D Object/Instance level segmetation maps can be obtained, combined that with Depth Map the 3D point cloud segmentation can be obtained. Further more the annotations can be exported in various popular formats like COCO, YOLO, Pix3D, KITTI, BOP.

<p float="left">
    <img src="./assets/Depth_and_trajectory.png" alt="Depth and Trajectory Example" width="300" height="180"> 
    <img src="./assets/segmentation_maps.png" alt="Depth and Trajectory Example" width="300" height="180"> 
    <img src="./assets/3D_bounding_boxes_and_point_cloud.png" alt="Depth and Trajectory Example" width="200" height="180"> 
</p>

## Videos 

<embed width="800" height="500" src="https://www.youtube.com/embed/inYH3Hqf-Ek" title="YouTube video player" frameborder="0" allow="accelerometer; autoplay; clipboard-write; encrypted-media; gyroscope; picture-in-picture" allowfullscreen>

<embed width="800" height="500" src="https://www.youtube.com/embed/Gp8cWECqigw" title="YouTube video player" frameborder="0" allow="accelerometer; autoplay; clipboard-write; encrypted-media; gyroscope; picture-in-picture" allowfullscreen>

## Use WareSynth Pipeline

The scripts here need blender to run, and you need to have the files set up as:
```bash
├── Project Directory
│   ├── Blender
│   │   ├── blender (executable)
│   ├── WareSynth (This repo)
│   │   ├── src
│   │   ├── objects (assets)
|   |   |   ├── primitives
```

* In order to generate the warehouse along with the front and top layouts:
```
bash genrateDataset
```

* If you want to also Generate Kitti, goto Constants files and make the GENERATE_KITTI flag true and then run the script
```
gedit scripts/pillared_warehouse/Constants.py
GENERATE_KITTI = True
bash genrateDataset
```

* The number of images and other configs of the warehouse can be altered by changing variables.