# Inbound Email $\rightarrow$ AWS SES $\rightarrow$ S3 $\rightarrow$ Lambda (Python) $\rightarrow$ Uber API

This is a great automation project for a Senior DevOps Leader to build with their son. Since you're already deep in the AWS/Python ecosystem, we can skip the "low-code" fluff and build a robust, serverless Event-Driven Architecture.The workflow is: Inbound Email $\rightarrow$ AWS SES $\rightarrow$ S3 $\rightarrow$ Lambda (Python) $\rightarrow$ Uber API.1. The Architecture (High Level)Trigger: Your son sends an email to a custom address (e.g., ride@yourdomain.com).Ingestion: Amazon SES receives the email and triggers an S3 Action to save the raw .eml file.Compute: An S3 Trigger invokes a Lambda function written in Python.  Execution: The Lambda parses the email body (looking for "2:35" or "4 PM"), calculates the pickup_time in Unix epoch format, and calls the Uber Rides API.

```
Simple Interaction for him
He just needs to send a short email:

To: ride@your-dev-domain.com

Subject: Ride

Body: Pick me up at 4 PM.

```