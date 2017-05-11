# pyblish-royalrender

## Setup

The environment variable ```RR_Root``` is required to point to the global installation of Royal Render.

## Usage

To use this extension you need to assign the ```royalrender``` family and have data in the ```royalrenderData``` data member on the instance you want to publish.

```royalrenderData``` is an dictionary that gets convert to RoyalRender's xml submission. Please read more about RoyalRender's xml; http://www.royalrender.de/help8/index.html?rrJobsubmitxmlfile.html.   
You can also get the xml data from an already submitted job in the rrControl application, by selecting a job and choosing "Jobs" > "Export selected Jobs as .xml".

Exported from rrControl:

```xml
<RR_Job_File syntax_version="6.0">
<Job>
    <Software>     Maya     </Software>
</Job>
</RR_Job_File>
```

Data that generated the above job:

```python
instance.data["royalrenderData"] = {
  "Software": "Maya"
}
```
