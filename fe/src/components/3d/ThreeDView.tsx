import { Canvas } from '@react-three/fiber';
import { Loader } from '@react-three/drei';
import { Suspense, useState, useEffect, useMemo } from 'react';
import { Stats } from '../../types';
import { Section } from './Section';
import { Scene } from './Scene';
import { Legend } from './Legend';
import * as THREE from 'three';

interface ThreeDViewProps {
  stats: Stats;
}

export function ThreeDView({ stats }: ThreeDViewProps) {
  const [hoveredSection, setHoveredSection] = useState<string | null>(null);
  const [selectedSection, setSelectedSection] = useState<string | null>(null);
  const [cameraTarget, setCameraTarget] = useState<THREE.Vector3>(new THREE.Vector3(0, 2, 0));

  // Group sensors by section
  const sections = useMemo(() => {
    return Object.entries(stats)
      .filter(([key, value]): value is [string, any] => 
        typeof value === 'object' && 
        value !== null && 
        'metadata' in value
      )
      .reduce((acc, [id, sensor]) => {
        const section = sensor.metadata.departement.split(' ')[2];
        if (!acc[section]) {
          acc[section] = [];
        }
        acc[section].push({ id, ...sensor });
        return acc;
      }, {} as Record<string, any[]>);
  }, [stats]);

  // Calculate section positions
  const sectionPositions = useMemo(() => {
    const sectionCount = Object.keys(sections).length;
    const radius = Math.max(sectionCount * 1.5, 10);
    
    return Object.keys(sections).reduce((acc, section, index) => {
      const angle = (index * Math.PI * 2) / sectionCount;
      acc[section] = new THREE.Vector3(
        Math.cos(angle) * radius,
        0,
        Math.sin(angle) * radius
      );
      return acc;
    }, {} as Record<string, THREE.Vector3>);
  }, [sections]);

  // Calculate section sizes based on sensor count
  const sectionSizes = useMemo(() => {
    return Object.entries(sections).reduce((acc, [section, sensorList]) => {
      const baseSize = 4;
      const sizeScale = Math.log(sensorList.length + 1) / Math.log(4);
      acc[section] = new THREE.Vector3(
        baseSize * sizeScale,
        baseSize * 0.8,
        baseSize * sizeScale
      );
      return acc;
    }, {} as Record<string, THREE.Vector3>);
  }, [sections]);

  // Update camera target when selection changes
  useEffect(() => {
    if (selectedSection && sectionPositions[selectedSection]) {
      const position = sectionPositions[selectedSection];
      setCameraTarget(new THREE.Vector3(position.x, 2, position.z));
    } else {
      setCameraTarget(new THREE.Vector3(0, 2, 0));
    }
  }, [selectedSection, sectionPositions]);

  return (
    <div className="relative h-[calc(100vh-12rem)] w-full bg-gray-900 rounded-lg overflow-hidden">
      <Canvas
        camera={{ position: [30, 30, 30], fov: 45 }}
        shadows
        dpr={[1, 2]}
      >
        <Suspense fallback={null}>
          <Scene cameraTarget={cameraTarget}>
            {Object.entries(sections).map(([section, sectionData]) => (
              <Section
                key={section}
                sectionNumber={section}
                position={sectionPositions[section]}
                size={sectionSizes[section]}
                sensors={sectionData}
                isHovered={hoveredSection === section}
                isSelected={selectedSection === section}
                onHover={() => setHoveredSection(section)}
                onUnhover={() => setHoveredSection(null)}
                onSelect={() => setSelectedSection(
                  selectedSection === section ? null : section
                )}
              />
            ))}
          </Scene>
        </Suspense>
      </Canvas>
      <Legend
        stats={stats}
        hoveredSection={hoveredSection}
        selectedSection={selectedSection}
        onSectionHover={setHoveredSection}
        onSectionSelect={setSelectedSection}
      />
      <Loader />
    </div>
  );
}