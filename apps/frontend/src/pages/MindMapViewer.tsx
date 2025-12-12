import React, { useState, useEffect, useRef } from 'react';
import {
  Box,
  VStack,
  HStack,
  Card,
  CardBody,
  CardHeader,
  Text,
  Button,
  Heading,
  useColorModeValue,
  Badge,
  useToast,
  Alert,
  AlertIcon,
  Spinner,
  Tabs,
  TabList,
  TabPanels,
  Tab,
  TabPanel,
  IconButton,
  Tooltip,
  Modal,
  ModalOverlay,
  ModalContent,
  ModalHeader,
  ModalBody,
  ModalCloseButton,
  useDisclosure,
  Input,
  Textarea,
} from '@chakra-ui/react';
import { FiZoomIn, FiZoomOut, FiRefreshCw, FiEdit, FiPlus } from 'react-icons/fi';
import { useAppStore } from '../store/useAppStore';
import { MindMapData, MindMapNode } from '../types';
import { apiService } from '../services/api';

interface MindMapNodeComponentProps {
  node: MindMapNode;
  onNodeClick: (node: MindMapNode) => void;
  onNodeEdit: (nodeId: string, newContent: string) => void;
  scale: number;
  isDark: boolean;
}

const MindMapNodeComponent: React.FC<MindMapNodeComponentProps> = ({
  node,
  onNodeClick,
  onNodeEdit,
  scale,
  isDark
}) => {
  const [isEditing, setIsEditing] = useState(false);
  const [editContent, setEditContent] = useState(node.content);
  const [showChildren, setShowChildren] = useState(node.expanded);

  const handleNodeClick = () => {
    onNodeClick(node);
    setShowChildren(!showChildren);
  };

  const handleEdit = (e: React.MouseEvent) => {
    e.stopPropagation();
    setIsEditing(true);
  };

  const handleSave = () => {
    onNodeEdit(node.id, editContent);
    setIsEditing(false);
  };

  const handleCancel = () => {
    setEditContent(node.content);
    setIsEditing(false);
  };

  const nodeStyle = {
    position: 'absolute' as const,
    left: node.x * scale,
    top: node.y * scale,
    transform: 'translate(-50%, -50%)',
    backgroundColor: node.color || (isDark ? '#4A5568' : '#3182CE'),
    color: 'white',
    padding: '8px 12px',
    borderRadius: '8px',
    cursor: 'pointer',
    fontSize: `${12 * scale}px`,
    minWidth: '80px',
    textAlign: 'center' as const,
    transition: 'all 0.2s ease',
    zIndex: node.id === 'root' ? 10 : 1,
    opacity: showChildren ? 1 : 0.7,
  };

  return (
    <>
      <Box
        style={nodeStyle}
        onClick={handleNodeClick}
        border={node.expanded ? '2px solid white' : '2px solid transparent'}
      >
        {isEditing ? (
          <Box>
            <Input
              size="sm"
              value={editContent}
              onChange={(e) => setEditContent(e.target.value)}
              onBlur={handleSave}
              onKeyDown={(e) => {
                if (e.key === 'Enter') handleSave();
                if (e.key === 'Escape') handleCancel();
              }}
              autoFocus
              bg="white"
              color="black"
            />
          </Box>
        ) : (
          <Box display="flex" alignItems="center" justifyContent="space-between">
            <Text>{node.content}</Text>
            <HStack spacing={1} ml={2}>
              <IconButton
                aria-label="Edit node"
                icon={<FiEdit />}
                size="xs"
                variant="ghost"
                onClick={handleEdit}
              />
              {node.children.length > 0 && (
                <Badge size="sm" bg="rgba(255,255,255,0.2)">
                  {node.children.length}
                </Badge>
              )}
            </HStack>
          </Box>
        )}
      </Box>
    </>
  );
};

export const MindMapViewer: React.FC = () => {
  const [mindMaps, setMindMaps] = useState<MindMapData[]>([]);
  const [currentMindMap, setCurrentMindMap] = useState<MindMapData | null>(null);
  const [nodes, setNodes] = useState<MindMapNode[]>([]);
  const [scale, setScale] = useState(1);
  const [selectedNode, setSelectedNode] = useState<MindMapNode | null>(null);
  const [isLoading, setIsLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);
  const [draggedNode, setDraggedNode] = useState<string | null>(null);

  const { isOpen, onOpen, onClose } = useDisclosure();
  const { darkMode } = useAppStore();
  const canvasRef = useRef<HTMLDivElement>(null);
  const toast = useToast();

  const cardBg = useColorModeValue('white', 'gray.800');
  const cardBorder = useColorModeValue('gray.200', 'gray.600');

  useEffect(() => {
    loadMindMaps();
  }, []);

  const loadMindMaps = async () => {
    setIsLoading(true);
    setError(null);
    
    try {
      const response = await apiService.getMindMaps();
      if (response.success && response.data) {
        setMindMaps(response.data);
        if (response.data.length > 0) {
          setCurrentMindMap(response.data[0]);
          setNodes(response.data[0].nodes);
        }
      }
    } catch (err) {
      setError('Failed to load mind maps');
      console.error('Mind map loading error:', err);
    } finally {
      setIsLoading(false);
    }
  };

  const handleMindMapSelect = (mindMapId: string) => {
    const mindMap = mindMaps.find(mm => mm.id === mindMapId);
    if (mindMap) {
      setCurrentMindMap(mindMap);
      setNodes(mindMap.nodes);
      setScale(1);
      setSelectedNode(null);
    }
  };

  const handleNodeClick = (node: MindMapNode) => {
    setSelectedNode(node);
    
    // Toggle expanded state
    setNodes(prev => prev.map(n => 
      n.id === node.id ? { ...n, expanded: !n.expanded } : n
    ));
  };

  const handleNodeEdit = (nodeId: string, newContent: string) => {
    setNodes(prev => prev.map(node => 
      node.id === nodeId ? { ...node, content: newContent } : node
    ));
    
    toast({
      title: 'Node Updated',
      status: 'success',
      duration: 1500,
    });
  };

  const handleZoomIn = () => {
    setScale(prev => Math.min(prev + 0.2, 3));
  };

  const handleZoomOut = () => {
    setScale(prev => Math.max(prev - 0.2, 0.3));
  };

  const handleResetZoom = () => {
    setScale(1);
  };

  const handleExport = () => {
    if (!currentMindMap) return;
    
    const exportData = {
      mindMap: currentMindMap,
      nodes,
      exportedAt: new Date().toISOString()
    };
    
    const blob = new Blob([JSON.stringify(exportData, null, 2)], {
      type: 'application/json'
    });
    
    const url = URL.createObjectURL(blob);
    const link = document.createElement('a');
    link.href = url;
    link.download = `${currentMindMap.title.replace(/\s+/g, '_')}.json`;
    link.click();
    
    URL.revokeObjectURL(url);
    
    toast({
      title: 'Mind Map Exported',
      description: 'Mind map data has been downloaded as JSON',
      status: 'success',
      duration: 3000,
    });
  };

  const handleCanvasClick = (e: React.MouseEvent) => {
    if (e.target === e.currentTarget) {
      setSelectedNode(null);
    }
  };

  if (isLoading) {
    return (
      <Box display="flex" justifyContent="center" alignItems="center" h="400px">
        <Spinner size="xl" />
      </Box>
    );
  }

  if (error) {
    return (
      <Alert status="error">
        <AlertIcon />
        {error}
        <Button ml={4} onClick={loadMindMaps}>Retry</Button>
      </Alert>
    );
  }

  if (mindMaps.length === 0) {
    return (
      <VStack spacing={4} align="center" py={10}>
        <Heading size="lg" color="gray.500">
          No mind maps available
        </Heading>
        <Text color="gray.500">
          Create some mind maps to get started!
        </Text>
        <Button colorScheme="brand">
          Create Mind Map
        </Button>
      </VStack>
    );
  }

  return (
    <Box>
      <VStack spacing={6} align="stretch">
        {/* Header */}
        <HStack justify="space-between" align="start">
          <Box>
            <Heading size="lg" mb={2}>Mind Map Viewer</Heading>
            <Text color="gray.600">Visualize and explore your knowledge structures</Text>
          </Box>
          
          <HStack spacing={2}>
            <Tooltip label="Zoom In">
              <IconButton
                aria-label="Zoom in"
                icon={<FiZoomIn />}
                onClick={handleZoomIn}
                isDisabled={scale >= 3}
              />
            </Tooltip>
            <Tooltip label="Zoom Out">
              <IconButton
                aria-label="Zoom out"
                icon={<FiZoomOut />}
                onClick={handleZoomOut}
                isDisabled={scale <= 0.3}
              />
            </Tooltip>
            <Tooltip label="Reset Zoom">
              <IconButton
                aria-label="Reset zoom"
                icon={<FiRefreshCw />}
                onClick={handleResetZoom}
                isDisabled={scale === 1}
              />
            </Tooltip>
            <Button onClick={handleExport} leftIcon={<FiPlus />}>
              Export
            </Button>
          </HStack>
        </HStack>

        <HStack spacing={6} align="start">
          {/* Mind Map Selection Sidebar */}
          <Box w="250px" flexShrink={0}>
            <Card bg={cardBg} border="1px" borderColor={cardBorder}>
              <CardHeader>
                <Heading size="sm">Mind Maps</Heading>
              </CardHeader>
              <CardBody p={0}>
                <Tabs 
                  orientation="vertical" 
                  onChange={(index) => handleMindMapSelect(mindMaps[index].id)}
                >
                  <TabList borderBottom="none">
                    {mindMaps.map((mindMap) => (
                      <Tab key={mindMap.id} w="full" textAlign="left">
                        {mindMap.title}
                      </Tab>
                    ))}
                  </TabList>
                </Tabs>
              </CardBody>
            </Card>
            
            {selectedNode && (
              <Card bg={cardBg} border="1px" borderColor={cardBorder} mt={4}>
                <CardHeader>
                  <Heading size="sm">Node Details</Heading>
                </CardHeader>
                <CardBody>
                  <VStack spacing={3} align="stretch">
                    <Text fontWeight="bold">{selectedNode.content}</Text>
                    <HStack justify="space-between">
                      <Text fontSize="sm" color="gray.600">Children:</Text>
                      <Badge>{selectedNode.children.length}</Badge>
                    </HStack>
                    <HStack justify="space-between">
                      <Text fontSize="sm" color="gray.600">Expanded:</Text>
                      <Badge colorScheme={selectedNode.expanded ? 'green' : 'gray'}>
                        {selectedNode.expanded ? 'Yes' : 'No'}
                      </Badge>
                    </HStack>
                  </VStack>
                </CardBody>
              </Card>
            )}
          </Box>

          {/* Main Mind Map Canvas */}
          <Box flex="1">
            <Card 
              bg={cardBg} 
              border="1px" 
              borderColor={cardBorder}
              minH="600px"
              position="relative"
              overflow="hidden"
            >
              <CardHeader>
                <HStack justify="space-between">
                  <Heading size="md">
                    {currentMindMap?.title || 'Select a Mind Map'}
                  </Heading>
                  <HStack>
                    <Badge colorScheme="blue">Scale: {Math.round(scale * 100)}%</Badge>
                    <Badge colorScheme="green">{nodes.length} nodes</Badge>
                  </HStack>
                </HStack>
              </CardHeader>
              
              <CardBody p={0}>
                <Box
                  ref={canvasRef}
                  w="100%"
                  h="500px"
                  position="relative"
                  bg={useColorModeValue('gray.50', 'gray.900')}
                  onClick={handleCanvasClick}
                  cursor="grab"
                  overflow="hidden"
                >
                  {/* Render connections between nodes */}
                  <svg 
                    width="100%" 
                    height="100%" 
                    style={{ position: 'absolute', top: 0, left: 0, pointerEvents: 'none' }}
                  >
                    {nodes.map(node => {
                      const parentNode = nodes.find(n => node.children.includes(node.id));
                      if (parentNode && parentNode.expanded) {
                        return (
                          <line
                            key={`${parentNode.id}-${node.id}`}
                            x1={parentNode.x * scale}
                            y1={parentNode.y * scale}
                            x2={node.x * scale}
                            y2={node.y * scale}
                            stroke={useColorModeValue('#A0AEC0', '#4A5568')}
                            strokeWidth={2}
                            opacity={0.6}
                          />
                        );
                      }
                      return null;
                    })}
                  </svg>

                  {/* Render nodes */}
                  {nodes
                    .filter(node => node.id === 'root' || nodes.find(n => n.children.includes(node.id))?.expanded)
                    .map(node => (
                      <MindMapNodeComponent
                        key={node.id}
                        node={node}
                        onNodeClick={handleNodeClick}
                        onNodeEdit={handleNodeEdit}
                        scale={scale}
                        isDark={darkMode}
                      />
                    ))}
                </Box>
              </CardBody>
            </Card>
          </Box>
        </HStack>
      </VStack>
    </Box>
  );
};
