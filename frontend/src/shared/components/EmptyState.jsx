import React from 'react';
import { Box, Typography, Button } from '@mui/material';
import { Inbox as InboxIcon } from '@mui/icons-material';

export default function EmptyState({ 
  title = 'Нет данных', 
  description = 'Здесь пока ничего нет',
  action,
  actionLabel,
  onAction,
  icon: Icon = InboxIcon 
}) {
  const IconComponent = React.isValidElement(Icon) ? () => Icon : Icon;
  
  return (
    <Box
      sx={{
        display: 'flex',
        flexDirection: 'column',
        alignItems: 'center',
        justifyContent: 'center',
        py: 8,
        px: 2,
        textAlign: 'center',
      }}
    >
      <Box
        sx={{
          width: 80,
          height: 80,
          borderRadius: '50%',
          bgcolor: 'action.hover',
          display: 'flex',
          alignItems: 'center',
          justifyContent: 'center',
          mb: 3,
        }}
      >
        {React.isValidElement(Icon) ? Icon : <IconComponent sx={{ fontSize: 40, color: 'text.secondary' }} />}
      </Box>
      <Typography variant="h6" fontWeight={600} gutterBottom>
        {title}
      </Typography>
      <Typography variant="body2" color="text.secondary" sx={{ maxWidth: 400, mb: 3 }}>
        {description}
      </Typography>
      {action || (actionLabel && onAction && (
        <Button variant="contained" onClick={onAction}>
          {actionLabel}
        </Button>
      ))}
    </Box>
  );
}
