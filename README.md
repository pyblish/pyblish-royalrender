# pyblish-royalrender

**CURRENTLY ONLY WINDOWS IS SUPPORTED**

## Setup

The environment variable ```RR_Root``` is required to point to the global installation of Royal Render.

## Usage

To use this extension you need to assign the ```royalrender``` family and have data in the ```royalrenderData``` or ```royalrenderJobs``` data member on the instance you want to publish.

### royalrenderData
```royalrenderData``` is a dictionary that gets convert to RoyalRender's xml submission. Please read more about RoyalRender's xml; http://www.royalrender.de/help8/index.html?rrJobsubmitxmlfile.html.   
You can also get the xml data from an already submitted job in the rrControl application, by selecting a job and choosing "Jobs" > "Export selected Jobs as .xml".

Exported from rrControl:

```xml
<RR_Job_File syntax_version="6.0">
<Job>
    <Software>     Maya     </Software>
    <Priority>     84     </Priority>
    <RRO_Overwriteexistingfiles>     true     </RRO_Overwriteexistingfiles>
</Job>
</RR_Job_File>
```

Data that generated the above job:

```python
instance.data["royalrenderData"] = {
  "Software": "Maya"
  "SubmitterParameter": [
      "Priority=1~84",
      "OverwriteExistingFiles=1~1"
  ]
}
```

### royalrenderJobs
```royalrenderData``` is a list of dictionaries to support submitting multiple jobs.

### Submission UI
You can also force the showing of the submission UI, by checking the ```Display Royal Render Submitter``` plugin.
