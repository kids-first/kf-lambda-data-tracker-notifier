ALL_EVENTS = """
query (
    $studyId: String,
    $fileId: String,
    $versionId: String,
    $createdAt_Gt: DateTime,
    $createdAt_Lt: DateTime,
    $user_Username: String,
    $eventType: String,
) {
    allEvents(
        study_KfId: $studyId,
        file_KfId: $fileId,
        version_KfId: $versionId,
        createdAt_Gt: $createdAt_Gt,
        createdAt_Lt: $createdAt_Lt,
        user_Username: $user_Username,
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
