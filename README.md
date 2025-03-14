# teams-notifications

Dummy workflows used to notify Microsoft Teams channels about events.

This repo can be used when we need to post an update into Microsoft Teams but the triggering event is not a GitHub actions. We do not have Teams webhooks available to us due to organizational policies. But the Teams/GitHub integration is available.

## Usage

### Triggering the Workflow

To use this you have to fire off the workflow using a `workflow_dispatch` event from your triggering source. There is example code in `trigger_workflow.py` that shows how to do this.

Inputs that can be provided are:

- Subject: The subject to be used as the run-name of the workflow (this will show up in Teams)
- Body: The body text to be posted in the workflow run's output (this will not show up in Teams)
- ID: A random ID number to be posted in a workflow run's step (see the "Getting the Run ID" section below)
- Failure: If set to true, this will cause the workflow to fail (this will show up in Teams)

### Subscribing to the Workflow

You can subscribe to this from a Teams channel using the [integration](https://github.com/integrations/microsoft-teams?tab=readme-ov-file#actions-workflow-notifications):

```
@GitHub subscribe NCIOCPL/teams-notifications workflows:{name: "Notify <My Channel>"}
```

### Re-Running the Workflow

If a workflow is re-run then the Teams integration will post an "Attempt #X" comment on the original thread it created. This can be useful if you want to know, in Teams, that an event has reoccurred.

To do this you have to re-run the workflow run, not send a new workflow event. There is example code for doing that in `trigger_rerun.sh` that illustrates how to use the run ID to re-run the workflow.


#### Getting the Run ID 

Because the GitHub workflow API endpoint is asynchronous, it will not return the run ID for you when you trigger it. Thus after triggering the workflow you have to call the workflow list endpoint to find the workflow run that you caused, then extract the run ID from that. The `trigger_workflow.py` also has example code on how to get the run ID from GitHub.