/**
 * Компонент для просмотра и управления вложениями дефекта
 */

import React, { useState } from 'react';
import {
  Box,
  Card,
  CardContent,
  Typography,
  IconButton,
  Dialog,
  DialogTitle,
  DialogContent,
  DialogActions,
  Button,
  Grid,
  Chip,
  Tooltip,
  CircularProgress,
  Alert
} from '@mui/material';
import {
  Download as DownloadIcon,
  Delete as DeleteIcon,
  Image as ImageIcon,
  PictureAsPdf as PdfIcon,
  Description as DocIcon,
  TableChart as ExcelIcon,
  InsertDriveFile as FileIcon,
  ZoomIn as ZoomInIcon,
  Close as CloseIcon
} from '@mui/icons-material';

interface Attachment {
  id: number;
  filename: string;
  file_type: string;
  file_size: number;
  file_url: string;
  uploaded_at: string;
  uploaded_by: {
    id: number;
    first_name: string;
    last_name: string;
  };
}

interface AttachmentViewerProps {
  attachments: Attachment[];
  onDelete?: (attachmentId: number) => Promise<void>;
  canDelete?: boolean;
}

export const AttachmentViewer: React.FC<AttachmentViewerProps> = ({
  attachments,
  onDelete,
  canDelete = false
}) => {
  const [selectedImage, setSelectedImage] = useState<string | null>(null);
  const [deletingId, setDeletingId] = useState<number | null>(null);

  const getFileIcon = (fileType: string) => {
    if (fileType.startsWith('image/')) {
      return <ImageIcon color="primary" />;
    } else if (fileType === 'application/pdf') {
      return <PdfIcon color="error" />;
    } else if (fileType.includes('document') || fileType.includes('word')) {
      return <DocIcon color="info" />;
    } else if (fileType.includes('sheet') || fileType.includes('excel')) {
      return <ExcelIcon color="success" />;
    } else {
      return <FileIcon color="action" />;
    }
  };

  const formatFileSize = (bytes: number): string => {
    if (bytes === 0) return '0 Bytes';
    const k = 1024;
    const sizes = ['Bytes', 'KB', 'MB', 'GB'];
    const i = Math.floor(Math.log(bytes) / Math.log(k));
    return parseFloat((bytes / Math.pow(k, i)).toFixed(2)) + ' ' + sizes[i];
  };

  const handleDownload = (attachment: Attachment) => {
    const link = document.createElement('a');
    link.href = attachment.file_url;
    link.download = attachment.filename;
    link.target = '_blank';
    document.body.appendChild(link);
    link.click();
    document.body.removeChild(link);
  };

  const handleDelete = async (attachmentId: number) => {
    if (!onDelete) return;
    
    setDeletingId(attachmentId);
    try {
      await onDelete(attachmentId);
    } catch (error) {
      console.error('Ошибка удаления вложения:', error);
    } finally {
      setDeletingId(null);
    }
  };

  const isImage = (fileType: string) => fileType.startsWith('image/');

  if (attachments.length === 0) {
    return (
      <Alert severity="info" variant="outlined">
        Нет вложений
      </Alert>
    );
  }

  return (
    <Box>
      <Grid container spacing={2}>
        {attachments.map((attachment) => (
          <Grid item xs={12} sm={6} md={4} key={attachment.id}>
            <Card
              sx={{
                height: '100%',
                display: 'flex',
                flexDirection: 'column',
                transition: 'transform 0.2s, box-shadow 0.2s',
                '&:hover': {
                  transform: 'translateY(-2px)',
                  boxShadow: 4
                }
              }}
            >
              <CardContent sx={{ flexGrow: 1, p: 2 }}>
                {/* Превью для изображений */}
                {isImage(attachment.file_type) && (
                  <Box
                    sx={{
                      position: 'relative',
                      width: '100%',
                      height: 120,
                      mb: 2,
                      overflow: 'hidden',
                      borderRadius: 1,
                      cursor: 'pointer'
                    }}
                    onClick={() => setSelectedImage(attachment.file_url)}
                  >
                    <img
                      src={attachment.file_url}
                      alt={attachment.filename}
                      style={{
                        width: '100%',
                        height: '100%',
                        objectFit: 'cover'
                      }}
                    />
                    <Box
                      sx={{
                        position: 'absolute',
                        top: 4,
                        right: 4,
                        backgroundColor: 'rgba(0,0,0,0.7)',
                        borderRadius: '50%',
                        p: 0.5
                      }}
                    >
                      <ZoomInIcon sx={{ color: 'white', fontSize: 16 }} />
                    </Box>
                  </Box>
                )}

                {/* Иконка файла для не-изображений */}
                {!isImage(attachment.file_type) && (
                  <Box display="flex" justifyContent="center" mb={2}>
                    <Box sx={{ fontSize: 48 }}>
                      {getFileIcon(attachment.file_type)}
                    </Box>
                  </Box>
                )}

                {/* Информация о файле */}
                <Typography
                  variant="subtitle2"
                  noWrap
                  title={attachment.filename}
                  gutterBottom
                >
                  {attachment.filename}
                </Typography>

                <Box display="flex" justifyContent="space-between" alignItems="center" mb={1}>
                  <Chip
                    label={formatFileSize(attachment.file_size)}
                    size="small"
                    variant="outlined"
                  />
                  <Typography variant="caption" color="text.secondary">
                    {new Date(attachment.uploaded_at).toLocaleDateString('ru-RU')}
                  </Typography>
                </Box>

                <Typography variant="caption" color="text.secondary" display="block">
                  Загрузил: {attachment.uploaded_by.first_name} {attachment.uploaded_by.last_name}
                </Typography>

                {/* Действия */}
                <Box display="flex" justifyContent="center" gap={1} mt={2}>
                  <Tooltip title="Скачать">
                    <IconButton
                      size="small"
                      onClick={() => handleDownload(attachment)}
                      color="primary"
                    >
                      <DownloadIcon />
                    </IconButton>
                  </Tooltip>

                  {isImage(attachment.file_type) && (
                    <Tooltip title="Увеличить">
                      <IconButton
                        size="small"
                        onClick={() => setSelectedImage(attachment.file_url)}
                        color="info"
                      >
                        <ZoomInIcon />
                      </IconButton>
                    </Tooltip>
                  )}

                  {canDelete && (
                    <Tooltip title="Удалить">
                      <IconButton
                        size="small"
                        onClick={() => handleDelete(attachment.id)}
                        color="error"
                        disabled={deletingId === attachment.id}
                      >
                        {deletingId === attachment.id ? (
                          <CircularProgress size={16} />
                        ) : (
                          <DeleteIcon />
                        )}
                      </IconButton>
                    </Tooltip>
                  )}
                </Box>
              </CardContent>
            </Card>
          </Grid>
        ))}
      </Grid>

      {/* Диалог просмотра изображения */}
      <Dialog
        open={!!selectedImage}
        onClose={() => setSelectedImage(null)}
        maxWidth="lg"
        fullWidth
      >
        <DialogTitle>
          <Box display="flex" justifyContent="space-between" alignItems="center">
            <Typography variant="h6">Просмотр изображения</Typography>
            <IconButton onClick={() => setSelectedImage(null)}>
              <CloseIcon />
            </IconButton>
          </Box>
        </DialogTitle>
        <DialogContent>
          {selectedImage && (
            <Box
              display="flex"
              justifyContent="center"
              alignItems="center"
              sx={{ minHeight: 400 }}
            >
              <img
                src={selectedImage}
                alt="Увеличенное изображение"
                style={{
                  maxWidth: '100%',
                  maxHeight: '70vh',
                  objectFit: 'contain'
                }}
              />
            </Box>
          )}
        </DialogContent>
        <DialogActions>
          <Button onClick={() => setSelectedImage(null)}>
            Закрыть
          </Button>
          {selectedImage && (
            <Button
              variant="contained"
              startIcon={<DownloadIcon />}
              onClick={() => {
                const link = document.createElement('a');
                link.href = selectedImage;
                link.download = 'image';
                link.target = '_blank';
                document.body.appendChild(link);
                link.click();
                document.body.removeChild(link);
              }}
            >
              Скачать
            </Button>
          )}
        </DialogActions>
      </Dialog>
    </Box>
  );
};
