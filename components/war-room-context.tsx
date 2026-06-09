"use client";

import React, { createContext, useContext, useState, ReactNode } from "react";

export type TenantProfile = {
  id: string;
  name: string;
  zip: string;
  county: string;
  radius: string;
  appointments: number;
  monitoredLines: string[];
};

export const TENANTS: TenantProfile[] = [
  { 
    id: "npn:123456", 
    name: "Austin Premier Insurance Group", 
    zip: "78701", 
    county: "Travis",
    radius: "25-Mile Radius",
    appointments: 14,
    monitoredLines: ["Property & Casualty", "Workers' Comp"]
  },
  { 
    id: "npn:654321", 
    name: "Dallas Elite Risk Partners", 
    zip: "75201", 
    county: "Dallas",
    radius: "50-Mile Radius",
    appointments: 8,
    monitoredLines: ["Commercial Auto", "Property & Casualty"]
  }
];

type WarRoomContextType = {
  activeTenant: TenantProfile;
  setActiveTenant: (tenantId: string) => void;
  isPublicParanoia: boolean;
};

const WarRoomContext = createContext<WarRoomContextType | undefined>(undefined);

export function WarRoomProvider({ 
  children, 
  initialTenantId,
  isPublicParanoia
}: { 
  children: ReactNode; 
  initialTenantId: string;
  isPublicParanoia: boolean;
}) {
  const [activeTenantId, setActiveTenantId] = useState(initialTenantId);
  const activeTenant = TENANTS.find(t => t.id === activeTenantId) || TENANTS[0];

  const setActiveTenant = (id: string) => {
    setActiveTenantId(id);
    // Ideally update URL or cookie here, but React state manages the UI sync for now.
    // For full SSR refresh, we can use router.push or window.location
  };

  return (
    <WarRoomContext.Provider value={{ activeTenant, setActiveTenant, isPublicParanoia }}>
      {children}
    </WarRoomContext.Provider>
  );
}

export function useWarRoom() {
  const context = useContext(WarRoomContext);
  if (context === undefined) {
    throw new Error("useWarRoom must be used within a WarRoomProvider");
  }
  return context;
}
