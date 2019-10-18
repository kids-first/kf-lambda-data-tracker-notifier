ALL_EVENTS = """
query (
    $studyId: String,
    $fileId: String,
    $versionId: String,
    $createdAt_Gt: DateTime,
    $createdAt_Lt: DateTime,
    $username: String,
    $eventType: String,
) {
    allEvents(
        studyKfId: $studyId,
        fileKfId: $fileId,
        versionKfId: $versionId,
        createdAfter: $createdAt_Gt,
        createdBefore: $createdAt_Lt,
        username: $username,
        eventType: $eventType,
    ) {
        edges {
            node {
                id
                eventType
                description
                createdAt
                user {
                    username
                    picture
                }
                file {
                    kfId
                    name
                }
                version {
                    kfId
                }
                study {
                    kfId
                }
            }
        }
    }
}
"""

ALL_USERS = """
{
allUsers {
edges {
  node {
    id
    username
    slackNotify
    slackMemberId
    studySubscriptions {
      edges {
        node {
          kfId
          name
        }
      }
    }
  }
}
}
}
"""
