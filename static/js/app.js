const {
  colors,
  CssBaseline,
  ThemeProvider,
  createTheme,
  Box,
  AppBar,
  Toolbar,
  Typography,
  Container,
  Paper,
  Button,
  List,
  ListItem,
  ListItemIcon,
  ListItemText,
  LinearProgress,
  Breadcrumbs,
  Link,
  TextField,
  ButtonGroup,
} = MaterialUI;

const theme = createTheme({
  palette: {
    primary: {
      main: '#1976d2',
    },
    secondary: {
      main: '#dc004e',
    },
  },
});

function App() {
  const [files, setFiles] = React.useState([]);
  const [path, setPath] = React.useState('');
  const [uploading, setUploading] = React.useState(false);
  const [uploadProgress, setUploadProgress] = React.useState(0);
  const [uploadStatus, setUploadStatus] = React.useState('');
  const [searchTerm, setSearchTerm] = React.useState('');
  const [sortBy, setSortBy] = React.useState('name');

  const loadFiles = async (newPath = '', search = '', sort = 'name') => {
    const res = await fetch(`/api/list?path=${encodeURIComponent(newPath)}&search=${encodeURIComponent(search)}&sort=${sort}`);
    const data = await res.json();
    setFiles(data.items);
    setPath(data.path);
  };

  React.useEffect(() => {
    loadFiles(path, searchTerm, sortBy);
  }, [path, searchTerm, sortBy]);

  const handleFileUpload = async (event) => {
    const selectedFiles = event.target.files;
    if (!selectedFiles || selectedFiles.length === 0) return;

    setUploading(true);
    setUploadProgress(0);
    setUploadStatus('Starting upload...');

    const formData = new FormData();
    for(const file of selectedFiles) {
        // Use the relative path for folder uploads, otherwise just the filename
        const filePath = file.webkitRelativePath || file.name;
        formData.append('files[]', file, filePath);
    }
    
    // Add the current directory path
    formData.append('path', path);

    // Create a new XHR request
    const xhr = new XMLHttpRequest();

    // Function to handle progress updates
    xhr.upload.onprogress = (event) => {
        if (event.lengthComputable) {
            const percentComplete = (event.loaded / event.total) * 100;
            setUploadProgress(percentComplete);
            setUploadStatus(`Uploading... ${Math.round(percentComplete)}%`);
        }
    };

    // Function to handle completion
    xhr.onload = () => {
        setUploading(false);
        if (xhr.status === 200) {
            setUploadStatus('Upload successful!');
            loadFiles(path, searchTerm, sortBy);
        } else {
            setUploadStatus(`Upload failed: ${xhr.statusText}`);
        }
    };

    // Function to handle errors
    xhr.onerror = () => {
        setUploading(false);
        setUploadStatus('An error occurred during the upload.');
    };

    xhr.open('POST', '/upload', true);
    xhr.send(formData);
  };
  
  const handlePathChange = (newPath) => {
    setPath(newPath);
  };
  
  const handleSortChange = (newSortBy) => {
    setSortBy(sortBy === newSortBy ? `${newSortBy}_desc` : newSortBy);
  };

  const renderBreadcrumbs = () => {
    const parts = path.split('/').filter(Boolean);
    let currentPath = '';
    return (
      <Breadcrumbs aria-label="breadcrumb">
        <Link color="inherit" href="#" onClick={() => handlePathChange('')}>Home</Link>
        {parts.map((part, index) => {
          currentPath += `/${part}`;
          const isLast = index === parts.length - 1;
          const pathOnClick = currentPath.substring(1);
          return isLast ? (
            <Typography key={currentPath} color="text.primary">{part}</Typography>
          ) : (
            <Link key={currentPath} color="inherit" href="#" onClick={() => handlePathChange(pathOnClick)}>{part}</Link>
          );
        })}
      </Breadcrumbs>
    );
  };

  return (
    <ThemeProvider theme={theme}>
      <CssBaseline />
      <AppBar position="static"><Toolbar><Typography variant="h6">LAN File Server</Typography></Toolbar></AppBar>
      <Container maxWidth="md" sx={{ mt: 4 }}>
        <Paper sx={{ p: 2, mb: 2 }}>
          <Typography variant="h5" component="h2" gutterBottom>Upload</Typography>
          <Box>
            <Button variant="contained" component="label" sx={{ mr: 2 }}>
              Choose Files
              <input type="file" hidden multiple onChange={handleFileUpload} />
            </Button>
            <Button variant="contained" component="label">
              Choose Folder
              <input type="file" hidden webkitdirectory="" directory="" multiple onChange={handleFileUpload} />
            </Button>
          </Box>
          {uploading && (
            <Box sx={{ width: '100%', mt: 2 }}>
              <Typography variant="body2" color="text.secondary">{uploadStatus}</Typography>
              <LinearProgress variant="determinate" value={uploadProgress} />
              <Typography variant="body2" color="text.secondary">{`${Math.round(uploadProgress)}%`}</Typography>
            </Box>
          )}
        </Paper>
        <Paper sx={{ p: 2 }}>
          <Box sx={{ display: 'flex', justifyContent: 'space-between', mb: 2 }}>
            <TextField label="Search" variant="outlined" size="small" value={searchTerm} onChange={(e) => setSearchTerm(e.target.value)} />
            <ButtonGroup variant="outlined">
              <Button onClick={() => handleSortChange('name')} variant={sortBy.startsWith('name') ? 'contained' : 'outlined'}>Name</Button>
              <Button onClick={() => handleSortChange('size')} variant={sortBy.startsWith('size') ? 'contained' : 'outlined'}>Size</Button>
              <Button onClick={() => handleSortChange('modified')} variant={sortBy.startsWith('modified') ? 'contained' : 'outlined'}>Modified</Button>
            </ButtonGroup>
          </Box>
          {renderBreadcrumbs()}
          <List>
            {files.map((item) => (
              <ListItem key={item.name} secondaryAction={item.is_dir ? 
                (<Button onClick={() => handlePathChange(path ? `${path}/${item.name}` : item.name)}>Open</Button>) : 
                (<Button href={path ? `/download/${encodeURIComponent(`${path}/${item.name}`)}` : `/download/${encodeURIComponent(item.name)}`}>Download</Button>)}
              >
                <ListItemIcon>{item.is_dir ? <span className="material-icons">folder</span> : <span className="material-icons">description</span>}</ListItemIcon>
                <ListItemText primary={item.name} secondary={item.is_dir ? null : `${(item.size / 1024).toFixed(2)} KB`} />
              </ListItem>
            ))}
          </List>
        </Paper>
      </Container>
    </ThemeProvider>
  );
}

ReactDOM.render(<App />, document.getElementById('root'));