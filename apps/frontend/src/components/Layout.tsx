import React from 'react';
import {
  Box,
  Flex,
  HStack,
  VStack,
  IconButton,
  Button,
  Text,
  useColorMode,
  useColorModeValue,
  Drawer,
  DrawerBody,
  DrawerHeader,
  DrawerOverlay,
  DrawerContent,
  DrawerCloseButton,
  useDisclosure,
  Avatar,
  Badge,
  Container,
} from '@chakra-ui/react';
import { HamburgerIcon, SunIcon, MoonIcon } from '@chakra-ui/icons';
import { FiHome, FiBookOpen, FiClock, FiBarChart3 } from 'react-icons/fi';
import { useAppStore } from '../store/useAppStore';
import { useNavigate, useLocation } from 'react-router-dom';

interface LayoutProps {
  children: React.ReactNode;
}

export const Layout: React.FC<LayoutProps> = ({ children }) => {
  const { isOpen, onOpen, onClose } = useDisclosure();
  const { colorMode, toggleColorMode } = useColorMode();
  const navigate = useNavigate();
  const location = useLocation();
  const { 
    darkMode, 
    setDarkMode, 
    currentView, 
    setCurrentView, 
    isOnline,
    stats,
    todayProgress
  } = useAppStore();

  const bg = useColorModeValue('white', 'gray.800');
  const borderColor = useColorModeValue('gray.200', 'gray.700');

  const navItems = [
    { path: '/', icon: FiHome, label: 'Dashboard', key: 'dashboard' },
    { path: '/review', icon: FiBookOpen, label: 'Review', key: 'review' },
    { path: '/quiz', icon: FiClock, label: 'Quiz', key: 'quiz' },
    { path: '/mindmap', icon: FiBarChart3, label: 'Mind Maps', key: 'mindmap' },
  ];

  const handleNavigation = (path: string, key: string) => {
    navigate(path);
    setCurrentView(key as any);
    onClose();
  };

  const SidebarContent = () => (
    <VStack spacing={4} align="stretch" p={4}>
      <Box>
        <Text fontSize="2xl" fontWeight="bold" color="brand.500">
          Cognisphere
        </Text>
        <Text fontSize="sm" color="gray.500">
          Study Dashboard
        </Text>
      </Box>

      {stats && (
        <Box p={3} bg={useColorModeValue('gray.50', 'gray.700')} borderRadius="md">
          <Text fontSize="sm" fontWeight="semibold" mb={2}>Today's Progress</Text>
          <Text fontSize="2xl" fontWeight="bold" color="brand.500">
            {todayProgress.toFixed(0)}%
          </Text>
          <Text fontSize="xs" color="gray.500">
            {stats.cardsReviewedToday} of {stats.cardsDueToday} cards
          </Text>
        </Box>
      )}

      <VStack spacing={2} align="stretch">
        {navItems.map((item) => (
          <Button
            key={item.key}
            leftIcon={<item.icon />}
            variant={location.pathname === item.path ? 'solid' : 'ghost'}
            justifyContent="flex-start"
            onClick={() => handleNavigation(item.path, item.key)}
          >
            {item.label}
          </Button>
        ))}
      </VStack>

      <Box mt="auto">
        <Flex align="center" gap={2} p={2}>
          <Badge colorScheme={isOnline ? 'green' : 'red'}>
            {isOnline ? 'Online' : 'Offline'}
          </Badge>
          <Button size="sm" variant="outline" onClick={toggleColorMode}>
            {colorMode === 'light' ? <MoonIcon /> : <SunIcon />}
          </Button>
        </Flex>
      </Box>
    </VStack>
  );

  return (
    <Box minH="100vh">
      {/* Desktop Sidebar */}
      <Box
        display={{ base: 'none', md: 'block' }}
        w="250px"
        pos="fixed"
        h="100vh"
        bg={bg}
        borderRight="1px"
        borderColor={borderColor}
        overflowY="auto"
      >
        <SidebarContent />
      </Box>

      {/* Mobile Drawer */}
      <Drawer isOpen={isOpen} placement="left" onClose={onClose}>
        <DrawerOverlay />
        <DrawerContent>
          <DrawerCloseButton />
          <DrawerHeader>Cognisphere</DrawerHeader>
          <DrawerBody p={0}>
            <SidebarContent />
          </DrawerBody>
        </DrawerContent>
      </Drawer>

      {/* Main Content */}
      <Box ml={{ base: 0, md: '250px' }}>
        {/* Header */}
        <Flex
          h="60px"
          align="center"
          justify="space-between"
          px={4}
          bg={bg}
          borderBottom="1px"
          borderColor={borderColor}
          position="sticky"
          top={0}
          zIndex={10}
        >
          <HStack spacing={4}>
            <IconButton
              display={{ base: 'flex', md: 'none' }}
              onClick={onOpen}
              variant="outline"
              aria-label="open menu"
              icon={<HamburgerIcon />}
            />
            <Text fontSize="lg" fontWeight="semibold">
              {navItems.find(item => item.path === location.pathname)?.label || 'Cognisphere'}
            </Text>
          </HStack>

          <HStack spacing={4}>
            <Button size="sm" variant="outline" onClick={toggleColorMode}>
              {colorMode === 'light' ? <MoonIcon /> : <SunIcon />}
            </Button>
            <Avatar size="sm" name="User" />
          </HStack>
        </Flex>

        {/* Page Content */}
        <Container maxW="container.xl" py={6}>
          {children}
        </Container>
      </Box>
    </Box>
  );
};
