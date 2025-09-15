/**
 * Компонент системы комментариев для дефектов
 */

import React, { useState } from 'react';
import {
  Box,
  Card,
  CardContent,
  TextField,
  Button,
  Avatar,
  Typography,
  Divider,
  IconButton,
  Menu,
  MenuItem,
  Chip,
  Paper,
} from '@mui/material';
import {
  Send,
  MoreVert,
  Edit,
  Delete,
  Reply,
  AttachFile,
  Image,
} from '@mui/icons-material';
import { formatDistanceToNow } from 'date-fns';
import { ru } from 'date-fns/locale';

interface Comment {
  id: number;
  author: {
    id: number;
    first_name: string;
    last_name: string;
    role: string;
  };
  content: string;
  created_at: string;
  updated_at: string;
  is_internal: boolean;
  attachments?: Array<{
    id: number;
    filename: string;
    url: string;
    type: string;
  }>;
  parent_id?: number;
}

interface DefectCommentsProps {
  defectId: number;
  comments: Comment[];
  onAddComment: (content: string, isInternal: boolean, files?: FileList) => void;
  onEditComment: (commentId: number, content: string) => void;
  onDeleteComment: (commentId: number) => void;
  currentUserId: number;
  canViewInternal?: boolean;
}

export const DefectComments: React.FC<DefectCommentsProps> = ({
  defectId,
  comments,
  onAddComment,
  onEditComment,
  onDeleteComment,
  currentUserId,
  canViewInternal = false,
}) => {
  const [newComment, setNewComment] = useState('');
  const [isInternal, setIsInternal] = useState(false);
  const [editingComment, setEditingComment] = useState<number | null>(null);
  const [editContent, setEditContent] = useState('');
  const [menuAnchor, setMenuAnchor] = useState<null | HTMLElement>(null);
  const [selectedComment, setSelectedComment] = useState<number | null>(null);
  const [replyToComment, setReplyToComment] = useState<number | null>(null);
  const [attachments, setAttachments] = useState<FileList | null>(null);

  const handleSubmitComment = () => {
    if (newComment.trim()) {
      onAddComment(newComment, isInternal, attachments || undefined);
      setNewComment('');
      setIsInternal(false);
      setAttachments(null);
      setReplyToComment(null);
    }
  };

  const handleEditComment = (commentId: number) => {
    const comment = comments.find(c => c.id === commentId);
    if (comment) {
      setEditingComment(commentId);
      setEditContent(comment.content);
    }
    setMenuAnchor(null);
  };

  const handleSaveEdit = () => {
    if (editingComment && editContent.trim()) {
      onEditComment(editingComment, editContent);
      setEditingComment(null);
      setEditContent('');
    }
  };

  const handleCancelEdit = () => {
    setEditingComment(null);
    setEditContent('');
  };

  const handleDeleteComment = (commentId: number) => {
    onDeleteComment(commentId);
    setMenuAnchor(null);
  };

  const handleMenuOpen = (event: React.MouseEvent<HTMLElement>, commentId: number) => {
    setMenuAnchor(event.currentTarget);
    setSelectedComment(commentId);
  };

  const handleMenuClose = () => {
    setMenuAnchor(null);
    setSelectedComment(null);
  };

  const handleFileUpload = (event: React.ChangeEvent<HTMLInputElement>) => {
    if (event.target.files) {
      setAttachments(event.target.files);
    }
  };

  const filteredComments = comments.filter(comment => 
    canViewInternal || !comment.is_internal
  );

  const getCommentThreads = () => {
    const threads: { parent: Comment; replies: Comment[] }[] = [];
    const parentComments = filteredComments.filter(c => !c.parent_id);
    
    parentComments.forEach(parent => {
      const replies = filteredComments.filter(c => c.parent_id === parent.id);
      threads.push({ parent, replies });
    });
    
    return threads;
  };

  const renderComment = (comment: Comment, isReply = false) => (
    <Card
      key={comment.id}
      elevation={isReply ? 1 : 2}
      sx={{ 
        mb: 2,
        ml: isReply ? 4 : 0,
        border: comment.is_internal ? '1px solid #ff9800' : 'none'
      }}
    >
      <CardContent>
        <Box display="flex" alignItems="flex-start" gap={2}>
          <Avatar sx={{ bgcolor: 'primary.main' }}>
            {comment.author.first_name[0]}{comment.author.last_name[0]}
          </Avatar>
          
          <Box flex={1}>
            <Box display="flex" alignItems="center" gap={1} mb={1}>
              <Typography variant="subtitle2" fontWeight="bold">
                {comment.author.first_name} {comment.author.last_name}
              </Typography>
              <Chip
                size="small"
                label={comment.author.role}
                color="primary"
                variant="outlined"
              />
              {comment.is_internal && (
                <Chip
                  size="small"
                  label="Внутренний"
                  color="warning"
                  variant="filled"
                />
              )}
              <Typography variant="caption" color="text.secondary">
                {formatDistanceToNow(new Date(comment.created_at), {
                  addSuffix: true,
                  locale: ru,
                })}
              </Typography>
            </Box>

            {editingComment === comment.id ? (
              <Box>
                <TextField
                  fullWidth
                  multiline
                  rows={3}
                  value={editContent}
                  onChange={(e) => setEditContent(e.target.value)}
                  variant="outlined"
                  size="small"
                />
                <Box display="flex" gap={1} mt={1}>
                  <Button size="small" onClick={handleSaveEdit}>
                    Сохранить
                  </Button>
                  <Button size="small" color="secondary" onClick={handleCancelEdit}>
                    Отмена
                  </Button>
                </Box>
              </Box>
            ) : (
              <>
                <Typography variant="body2" sx={{ mb: 1 }}>
                  {comment.content}
                </Typography>
                
                {comment.attachments && comment.attachments.length > 0 && (
                  <Box display="flex" gap={1} flexWrap="wrap" mb={1}>
                    {comment.attachments.map(attachment => (
                      <Chip
                        key={attachment.id}
                        icon={attachment.type.startsWith('image/') ? <Image /> : <AttachFile />}
                        label={attachment.filename}
                        variant="outlined"
                        size="small"
                        onClick={() => window.open(attachment.url, '_blank')}
                        clickable
                      />
                    ))}
                  </Box>
                )}
                
                <Box display="flex" alignItems="center" gap={1}>
                  <Button
                    size="small"
                    startIcon={<Reply />}
                    onClick={() => setReplyToComment(comment.id)}
                  >
                    Ответить
                  </Button>
                </Box>
              </>
            )}
          </Box>
          
          {comment.author.id === currentUserId && (
            <IconButton
              size="small"
              onClick={(e) => handleMenuOpen(e, comment.id)}
            >
              <MoreVert />
            </IconButton>
          )}
        </Box>
      </CardContent>
    </Card>
  );

  return (
    <Box>
      <Typography variant="h6" mb={2}>
        Комментарии ({filteredComments.length})
      </Typography>

      {/* Список комментариев */}
      <Box mb={3}>
        {getCommentThreads().map(thread => (
          <Box key={thread.parent.id} mb={3}>
            {renderComment(thread.parent)}
            {thread.replies.map(reply => renderComment(reply, true))}
          </Box>
        ))}
        
        {filteredComments.length === 0 && (
          <Paper sx={{ p: 3, textAlign: 'center' }}>
            <Typography color="text.secondary">
              Комментариев пока нет. Будьте первым!
            </Typography>
          </Paper>
        )}
      </Box>

      {/* Форма добавления комментария */}
      <Paper elevation={2} sx={{ p: 2 }}>
        <Typography variant="subtitle1" mb={2}>
          {replyToComment ? 'Ответить на комментарий' : 'Добавить комментарий'}
        </Typography>
        
        <TextField
          fullWidth
          multiline
          rows={4}
          placeholder="Введите комментарий..."
          value={newComment}
          onChange={(e) => setNewComment(e.target.value)}
          variant="outlined"
          sx={{ mb: 2 }}
        />
        
        {attachments && (
          <Box mb={2}>
            <Typography variant="caption" color="text.secondary">
              Прикреплённые файлы:
            </Typography>
            <Box display="flex" gap={1} flexWrap="wrap" mt={1}>
              {Array.from(attachments).map((file, index) => (
                <Chip
                  key={index}
                  label={file.name}
                  variant="outlined"
                  size="small"
                  onDelete={() => setAttachments(null)}
                />
              ))}
            </Box>
          </Box>
        )}
        
        <Box display="flex" alignItems="center" justifyContent="space-between">
          <Box display="flex" alignItems="center" gap={2}>
            <input
              accept="*/*"
              style={{ display: 'none' }}
              id="file-upload"
              type="file"
              multiple
              onChange={handleFileUpload}
            />
            <label htmlFor="file-upload">
              <Button
                component="span"
                startIcon={<AttachFile />}
                size="small"
                variant="outlined"
              >
                Прикрепить файл
              </Button>
            </label>
            
            {canViewInternal && (
              <Button
                size="small"
                variant={isInternal ? "contained" : "outlined"}
                color="warning"
                onClick={() => setIsInternal(!isInternal)}
              >
                Внутренний комментарий
              </Button>
            )}
          </Box>
          
          <Button
            variant="contained"
            endIcon={<Send />}
            onClick={handleSubmitComment}
            disabled={!newComment.trim()}
          >
            Отправить
          </Button>
        </Box>
        
        {replyToComment && (
          <Button
            size="small"
            color="secondary"
            onClick={() => setReplyToComment(null)}
            sx={{ mt: 1 }}
          >
            Отменить ответ
          </Button>
        )}
      </Paper>

      {/* Меню действий */}
      <Menu
        anchorEl={menuAnchor}
        open={Boolean(menuAnchor)}
        onClose={handleMenuClose}
      >
        <MenuItem onClick={() => selectedComment && handleEditComment(selectedComment)}>
          <Edit fontSize="small" sx={{ mr: 1 }} />
          Редактировать
        </MenuItem>
        <MenuItem 
          onClick={() => selectedComment && handleDeleteComment(selectedComment)}
          sx={{ color: 'error.main' }}
        >
          <Delete fontSize="small" sx={{ mr: 1 }} />
          Удалить
        </MenuItem>
      </Menu>
    </Box>
  );
};

export default DefectComments;