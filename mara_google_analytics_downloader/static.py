"""Contain static data from the Google Analytics API"""

# The possible metrics
# reference: https://ga-dev-tools.appspot.com/dimensions-metrics-explorer/?
METRICS = [
    # User
    'ga:users',
    'ga:newUsers',
    'ga:percentNewSessions',
    'ga:1dayUsers',
    'ga:7dayUsers',
    'ga:14dayUsers',
    'ga:28dayUsers',
    'ga:30dayUsers',
    'ga:sessionsPerUser',

    # Session
    'ga:sessions',
    'ga:bounces',
    'ga:bounceRate',
    'ga:sessionDuration',
    'ga:avgSessionDuration',
    'ga:uniqueDimensionCombinations',

    # Session
    'ga:hits',

    # Traffic Sources
    'ga:organicSearches',

    # Adwords
    'ga:impressions',
    'ga:adClicks',
    'ga:adCost',
    'ga:CPM',
    'ga:CPC',
    'ga:CTR',
    'ga:costPerTransaction',
    'ga:costPerGoalConversion',
    'ga:costPerConversion',
    'ga:RPC',
    'ga:ROAS'

    # TODO: not all metrics are added here
]

# The possible dimensions
DIMENSIONS = [
    # User
    'ga:userType',
    'ga:sessionCount',
    'ga:daysSinceLastSession',
    'ga:userDefinedValue',
    'ga:userBucket',

    # Session
    'ga:sessionDurationBucket',

    # Traffic Sources
    'ga:referralPath',
    'ga:fullReferrer',
    'ga:campaign',
    'ga:source',
    'ga:medium',
    'ga:sourceMedium',
    'ga:keyword',
    'ga:adContent',
    'ga:socialNetwork',
    'ga:hasSocialSourceReferral',
    'ga:campaignCode',

    # Adwords
    'ga:adGroup',
    'ga:adSlot',
    'ga:adDistributionNetwork',
    'ga:adMatchType',
    'ga:adKeywordMatchType',
    'ga:adMatchedQuery',
    'ga:adPlacementDomain',
    'ga:adPlacementUrl',
    'ga:adFormat',
    'ga:adTargetingType',
    'ga:adTargetingOption',
    'ga:adDisplayUrl',
    'ga:adDestinationUrl',
    'ga:adwordsCustomerID',
    'ga:adwordsCampaignID',
    'ga:adwordsAdGroupID',
    'ga:adwordsCreativeID',
    'ga:adwordsCriteriaID',
    'ga:adQueryWordCount',
    'ga:isTrueViewVideoAd'

    # TODO: not all dimensions are added here
]
