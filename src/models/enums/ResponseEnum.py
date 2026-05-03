from enum import Enum
class ResponseSignal(Enum):
    FILE_TYPE_NOT_SUPPORTED = 'file type not supported'
    FILE_SIZE_EXCEEDS_LIMIT = 'file size exceeds the maximum limit'
    FILE_UPLOAD_SUCCESS = 'file uploaded successfully'
    FILE_UPLOAD_FAILED = 'file upload failed'
    FILE_VALIDATION_SUCCESS = 'file validation successful'
    PROCESSING_FAILED = 'file processing failed'
    PROCESSING_SUCCESS = 'file processing successful'
  