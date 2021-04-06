# WareSynth

 A procedural synthetic  data  generation pipeline  that  can  be  used  to  generate  3D  warehouse  scenes and  automate  the  process  of  data  capture  and  generating corresponding  annotation.

## A Sample Warehouse

<img src="./assets/tes.png" alt="Depth and Trajectory Example" > 

### WareSynth Synthetic Warehouse Generation Pipeline is a part of the project: "RackLay: Multi-Layer Layout Estimation for Warehouse Racks" 
## Link to [arxiv Paper](https://arxiv.org/abs/2103.09174), [RackLay](https://avinash2468.github.io/RackLay/) 
## Link to [Dataset](https://drive.google.com/drive/folders/1-GizhhfVOeyITYK0nIYpoyQPgtgALHvG?usp=sharing) generated using WareSynth (used for training RackLay network)


## Videos 

<embed width="800" height="500" src="https://www.youtube.com/embed/inYH3Hqf-Ek" title="YouTube video player" frameborder="0" allow="accelerometer; autoplay; clipboard-write; encrypted-media; gyroscope; picture-in-picture" allowfullscreen>

<embed width="800" height="500" src="https://www.youtube.com/embed/Gp8cWECqigw" title="YouTube video player" frameborder="0" allow="accelerometer; autoplay; clipboard-write; encrypted-media; gyroscope; picture-in-picture" allowfullscreen>

## Capabilities of WareSynth

- Capture camera positions along with the intrinsic and extrinsic parameters for each view.
- Extract 2D annotations such as 2D bounding boxes and semantic and instance segmentation masks of the objects.  
- Obtain the 3D positions, orientations and 3D bounding boxes for all objects present in the camera FOV, along with depth maps and normal information. 
- Our pipeline can also be used to obtain stereo-information. 
- The annotations can be exported in various popular formats like COCO, YOLO, Pix3D, KITTI, BOP as needed by the user.

<p float="center">
    <img src="./assets/Depth_and_trajectory.png" alt="Depth and Trajectory Example" width="300" height="180"> 
    <img src="./assets/segmentation_maps.png" alt="Depth and Trajectory Example" width="300" height="180"> 
    <img src="./assets/3D_bounding_boxes_and_point_cloud.png" alt="Depth and Trajectory Example" width="200" height="180"> 
</p>
