"""
Parse SALT output files to extract tracking information.
Compare IC/CP/MOC tracking methods for consistency.
Cross-check with input TDT .dat file.

Issue: Missing region in SALT tracking - investigate differences between methods.
"""

import os
import re
from dataclasses import dataclass, field
from typing import Dict, List, Optional, Tuple
from pathlib import Path


@dataclass
class SALTTrackingData:
    """Data structure to hold parsed SALT tracking information."""
    title: str = ""
    tracking_type: str = ""  # PIJ, MOC, or MULTICELL (IC)
    
    # State vector parameters
    nreg: int = 0           # Number of regions
    kpn: int = 0            # Number of unknowns
    ilk: int = 0            # Leakage present/absent
    nbmix: int = 0          # Maximum number of mixtures
    nsurf: int = 0          # Number of outer surfaces
    method: int = 0         # 4=PIJ/MOC, 5=MULTICELL
    nang: int = 0           # Number of tracking angles
    ndim: int = 0           # Number of dimensions
    ntline: int = 0         # Total number of tracks
    nmacro: int = 0         # Number of macro geometries
    ijat: int = 0           # Additional interface current components
    nmix: int = 0           # Perimeter elements in macro geometries
    
    # Geometry data
    nb_elem: int = 0        # Number of elements
    nb_node: int = 0        # Number of nodes
    nb_surf2: int = 0       # Number of surfaces (type 2)
    
    # Merged data
    merged_regions: int = 0
    merged_surfaces: int = 0
    merged_nodes: int = 0
    
    # Arrays
    volumes: List[float] = field(default_factory=list)
    matalb: List[int] = field(default_factory=list)    # Material albedo
    keymrg: List[int] = field(default_factory=list)    # Key merge
    icode: List[int] = field(default_factory=list)     # Boundary codes
    galbed: List[float] = field(default_factory=list)  # Albedo values
    
    # Tracking quality
    rms_error: float = 0.0
    max_error: float = 0.0
    avg_error: float = 0.0
    
    # MACRO geometry info (for IC method)
    macro_flux_count: int = 0
    perimeter_elements: List[str] = field(default_factory=list)


@dataclass 
class TDTDatData:
    """Data structure to hold parsed TDT .dat file information."""
    typge: int = 0          # Geometry type
    nbfo: int = 0           # Number of folds
    node: int = 0           # Number of nodes
    elem: int = 0           # Number of elements
    macr: int = 0           # Number of macros
    nreg: int = 0           # Number of regions
    z: int = 0
    mac2: int = 0
    
    eps: float = 1e-5
    eps0: float = 1e-5
    
    flux_region_mapping: List[int] = field(default_factory=list)
    macro_names: List[str] = field(default_factory=list)
    
    # Element connectivity: elem_id -> (type, neighbor1, neighbor2)
    elements: Dict[int, Tuple[int, int, int]] = field(default_factory=dict)
    # Element geometry: elem_id -> (x, y, dx, dy)
    element_coords: Dict[int, Tuple[float, float, float, float]] = field(default_factory=dict)
    
    # Material assignment per region
    materials: List[int] = field(default_factory=list)
    material_names: List[str] = field(default_factory=list)
    
    # Boundary conditions
    bc_default: int = 0
    bc_nbbcda: int = 0
    bc_allsur: int = 0
    albedo: float = 1.0


class SALTOutputParser:
    """Parser for SALT module output files."""
    
    def __init__(self, filepath: str):
        self.filepath = filepath
        self.content = ""
        self.data = SALTTrackingData()
        
    def parse(self) -> SALTTrackingData:
        """Parse the SALT output file and return structured data."""
        with open(self.filepath, 'r') as f:
            self.content = f.read()
        
        self._parse_title()
        self._parse_tracking_type()
        self._parse_geometry_info()
        self._parse_merged_info()
        self._parse_volumes()
        self._parse_matalb()
        self._parse_keymrg()
        self._parse_icode()
        self._parse_galbed()
        self._parse_tracking_errors()
        self._parse_state_vector()
        self._parse_macro_info()
        
        return self.data
    
    def _parse_title(self):
        """Extract the title from SALT output."""
        # Title appears after the SALT banner
        match = re.search(r'LLLLLLL   TT\s*\n\s*\n\s*(.+?)\s*\n', self.content)
        if match:
            self.data.title = match.group(1).strip()
    
    def _parse_tracking_type(self):
        """Determine tracking type from output."""
        if "multicell surfacic tracking" in self.content.lower():
            self.data.tracking_type = "MULTICELL_IC"
        elif "PIJ or MOC tracking" in self.content:
            if "MOC" in self.data.title.upper():
                self.data.tracking_type = "MOC"
            elif "CP" in self.data.title.upper():
                self.data.tracking_type = "CP"
            else:
                self.data.tracking_type = "PIJ_MOC"
        else:
            self.data.tracking_type = "UNKNOWN"
    
    def _parse_geometry_info(self):
        """Parse basic geometry dimensions."""
        # Parse from "SEEKS => dimensions for geometry" section
        match = re.search(
            r'\*\s*typge,\s*nbfo,\s*node,\s*elem,\s*macr,\s*nreg.*?\n\s*(\d+)\s+(\d+)\s+(\d+)\s+(\d+)\s+(\d+)\s+(\d+)',
            self.content
        )
        if match:
            self.data.nb_node = int(match.group(3))
            self.data.nb_elem = int(match.group(4))
    
    def _parse_merged_info(self):
        """Parse merged regions/surfaces/nodes info."""
        match = re.search(
            r'number of merged regions,surfaces,nodes\s+(\d+)\s+(\d+)\s+(\d+)',
            self.content
        )
        if match:
            self.data.merged_regions = int(match.group(1))
            self.data.merged_surfaces = int(match.group(2))
            self.data.merged_nodes = int(match.group(3))
    
    def _parse_volumes(self):
        """Parse VOLUME section."""
        match = re.search(r'VOLUME\s+([\d\.\-DE\+\s]+?)(?=\n\s*-{10,})', self.content)
        if match:
            vol_str = match.group(1)
            # Parse scientific notation values
            values = re.findall(r'[\d\.\-]+[DE][\+\-]\d+', vol_str)
            self.data.volumes = [float(v.replace('D', 'E')) for v in values]
    
    def _parse_matalb(self):
        """Parse MATALB (material albedo) section."""
        match = re.search(r'MATALB\s+([\d\s\-]+?)(?=\n\s*-{10,})', self.content)
        if match:
            mat_str = match.group(1)
            values = re.findall(r'-?\d+', mat_str)
            self.data.matalb = [int(v) for v in values]
    
    def _parse_keymrg(self):
        """Parse KEYMRG (key merge) section."""
        match = re.search(r'KEYMRG\s+([\d\s\-]+?)(?=\n\s*-{10,})', self.content)
        if match:
            key_str = match.group(1)
            values = re.findall(r'-?\d+', key_str)
            self.data.keymrg = [int(v) for v in values]
    
    def _parse_icode(self):
        """Parse ICODE (boundary codes) section."""
        match = re.search(r'ICODE\s+([\d\s\-]+?)(?=\n\s*-{10,})', self.content)
        if match:
            code_str = match.group(1)
            values = re.findall(r'-?\d+', code_str)
            self.data.icode = [int(v) for v in values]
    
    def _parse_galbed(self):
        """Parse GALBED (albedo) section."""
        match = re.search(r'GALBED\s+([\d\.\-E\+\s]+)', self.content)
        if match:
            alb_str = match.group(1)
            values = re.findall(r'[\d\.\-]+E[\+\-]\d+', alb_str)
            self.data.galbed = [float(v) for v in values]
    
    def _parse_tracking_errors(self):
        """Parse tracking quality errors."""
        match = re.search(
            r'SALTLS: Global RMS, maximum and average errors \(%\).*?:\s+([\d\.\-]+)\s+([\d\.\-]+)\s+([\d\.\-]+)',
            self.content
        )
        if match:
            self.data.rms_error = float(match.group(1))
            self.data.max_error = float(match.group(2))
            self.data.avg_error = float(match.group(3))
    
    def _parse_state_vector(self):
        """Parse STATE VECTOR section."""
        state_patterns = {
            'nreg': r'NREG\s+(\d+)',
            'kpn': r'KPN\s+(\d+)',
            'ilk': r'ILK\s+(\d+)',
            'nbmix': r'NBMIX\s+(\d+)',
            'nsurf': r'NSURF\s+(\d+)',
            'method': r'METHOD\s+(\d+)',
            'nang': r'NANG\s+(\d+)',
            'ndim': r'NDIM\s+(\d+)',
            'ntline': r'NTLINE\s+(\d+)',
            'nmacro': r'NMACRO\s+(\d+)',
            'ijat': r'IJAT\s+(\d+)',
            'nmix': r'NMIX\s+(\d+)',
        }
        
        for attr, pattern in state_patterns.items():
            match = re.search(pattern, self.content)
            if match:
                setattr(self.data, attr, int(match.group(1)))
    
    def _parse_macro_info(self):
        """Parse MACRO geometry info (for IC method)."""
        match = re.search(r'MUSACG: number of flux in (\w+)=\s*(\d+)', self.content)
        if match:
            self.data.macro_flux_count = int(match.group(2))
        
        # Parse perimeter elements
        perimeter_matches = re.findall(r'S\d{6}', self.content)
        self.data.perimeter_elements = list(set(perimeter_matches))


class TDTDatParser:
    """Parser for TDT .dat input files (both GLOW and GEO formats)."""
    
    def __init__(self, filepath: str):
        self.filepath = filepath
        self.content = ""
        self.lines = []
        self.data = TDTDatData()
        self.is_geo_format = False
        
    def parse(self) -> TDTDatData:
        """Parse the TDT .dat file and return structured data."""
        with open(self.filepath, 'r') as f:
            self.content = f.read()
            self.lines = self.content.split('\n')
        
        # Detect format type
        self.is_geo_format = self._detect_format()
        
        if self.is_geo_format:
            self._parse_geo_format()
        else:
            self._parse_glow_format()
        
        return self.data
    
    def _detect_format(self) -> bool:
        """Detect if the file is in GEO format (has BEGIN marker)."""
        for line in self.lines[:10]:
            if line.strip() == 'BEGIN':
                return True
        return False
    
    def _parse_geo_format(self):
        """Parse GEO-generated .dat file format."""
        self._parse_geo_header()
        self._parse_geo_flux_regions()
        self._parse_geo_elements()
        self._parse_geo_materials()
    
    def _parse_geo_header(self):
        """Parse header in GEO format."""
        for i, line in enumerate(self.lines):
            if '*typgeo' in line:
                # Next line contains values
                values_line = self.lines[i + 1].strip()
                values = values_line.split()
                if len(values) >= 6:
                    self.data.typge = int(values[0])
                    self.data.nbfo = int(values[1])
                    self.data.node = int(values[2])
                    self.data.elem = int(values[3])
                    self.data.macr = int(values[4])
                    self.data.nreg = int(values[5])
                break
        
        # Parse epsilon
        for i, line in enumerate(self.lines):
            if '*eps' in line:
                values_line = self.lines[i + 1].strip()
                try:
                    self.data.eps = float(values_line)
                except ValueError:
                    pass
                break
    
    def _parse_geo_flux_regions(self):
        """Parse flux region mapping in GEO format."""
        in_merge_section = False
        flux_values = []
        
        for i, line in enumerate(self.lines):
            if '*merge' in line:
                in_merge_section = True
                continue
            if in_merge_section:
                stripped = line.strip()
                if stripped.startswith('*') or not stripped:
                    break
                values = stripped.split()
                flux_values.extend([int(v) for v in values])
        
        self.data.flux_region_mapping = flux_values
    
    def _parse_geo_elements(self):
        """Parse element definitions in GEO format."""
        i = 0
        while i < len(self.lines):
            line = self.lines[i].strip()
            
            # Look for element definition
            match = re.match(r'elem\s*=\s*(\d+)', line, re.IGNORECASE)
            if match:
                elem_id = int(match.group(1))
                
                # Skip to type line
                i += 1
                while i < len(self.lines) and '*type' not in self.lines[i]:
                    i += 1
                
                # Parse type and nodes
                i += 1
                if i < len(self.lines):
                    type_line = self.lines[i].strip()
                    type_values = type_line.split()
                    if len(type_values) >= 3:
                        elem_type = int(type_values[0])
                        node_minus = int(type_values[1])
                        node_plus = int(type_values[2])
                        self.data.elements[elem_id] = (elem_type, node_minus, node_plus)
                
                # Skip to coordinates line
                i += 1
                while i < len(self.lines) and '*cx' not in self.lines[i]:
                    i += 1
                
                # Parse coordinates
                i += 1
                if i < len(self.lines):
                    coord_line = self.lines[i].strip()
                    coord_values = coord_line.split()
                    if len(coord_values) >= 4:
                        coords = tuple(float(v) for v in coord_values[:4])
                        self.data.element_coords[elem_id] = coords
            i += 1
    
    def _parse_geo_materials(self):
        """Parse materials in GEO format."""
        # Find material names
        mat_names = []
        in_material_names = False
        
        for i, line in enumerate(self.lines):
            if '*mat_names' in line.lower():
                in_material_names = True
                continue
            if in_material_names:
                stripped = line.strip()
                if stripped.startswith('*') or not stripped or 'medium number' in stripped.lower():
                    break
                # Each non-empty line is a material name
                mat_names.append(stripped)
        
        self.data.material_names = mat_names
        
        # Parse medium numbers per region
        materials = []
        in_medium_section = False
        
        for i, line in enumerate(self.lines):
            if '*mix' in line.lower() and 'medium number' in self.lines[i-1].lower() if i > 0 else False:
                in_medium_section = True
                continue
            if 'medium number per region' in line.lower():
                in_medium_section = True
                # Skip to next line with *mix
                continue
            if in_medium_section:
                stripped = line.strip()
                if stripped.startswith('*mix'):
                    continue
                if stripped.startswith('*') or 'boundary' in stripped.lower():
                    break
                values = stripped.split()
                for v in values:
                    try:
                        materials.append(int(v))
                    except ValueError:
                        pass
        
        self.data.materials = materials
    
    def _parse_glow_format(self):
        """Parse GLOW-generated .dat file format."""
        self._parse_header()
        self._parse_flux_regions()
        self._parse_elements()
        self._parse_materials()
        self._parse_boundary_conditions()
    
    def _parse_header(self):
        """Parse header with geometry dimensions."""
        for i, line in enumerate(self.lines):
            if 'typge, nbfo, node, elem, macr, nreg' in line:
                # Next line contains values
                values_line = self.lines[i + 1].strip()
                values = [int(v.strip()) for v in values_line.split(',') if v.strip()]
                if len(values) >= 6:
                    self.data.typge = values[0]
                    self.data.nbfo = values[1]
                    self.data.node = values[2]
                    self.data.elem = values[3]
                    self.data.macr = values[4]
                    self.data.nreg = values[5]
                    if len(values) >= 8:
                        self.data.z = values[6]
                        self.data.mac2 = values[7]
                break
        
        # Parse epsilon values
        for i, line in enumerate(self.lines):
            if 'eps' in line.lower() and 'eps0' in line.lower():
                values_line = self.lines[i + 1].strip()
                values = re.findall(r'[\d\.\-]+E[\+\-]\d+', values_line)
                if len(values) >= 2:
                    self.data.eps = float(values[0])
                    self.data.eps0 = float(values[1])
                break
    
    def _parse_flux_regions(self):
        """Parse flux region mapping."""
        in_flux_section = False
        flux_values = []
        
        for line in self.lines:
            if 'flux region number per geometry region' in line:
                in_flux_section = True
                continue
            if in_flux_section:
                if line.strip().startswith('*'):
                    break
                values = re.findall(r'\d+', line)
                flux_values.extend([int(v) for v in values])
        
        self.data.flux_region_mapping = flux_values
    
    def _parse_elements(self):
        """Parse element definitions with connectivity."""
        elem_pattern = re.compile(r'\*\s*ELEM\s+(\d+)\s+line segment')
        
        i = 0
        while i < len(self.lines):
            match = elem_pattern.search(self.lines[i])
            if match:
                elem_id = int(match.group(1))
                # Next line contains: type, neighbor1, neighbor2
                i += 1
                conn_line = self.lines[i].strip()
                conn_values = [int(v.strip()) for v in conn_line.split(',') if v.strip()]
                if len(conn_values) >= 3:
                    self.data.elements[elem_id] = (conn_values[0], conn_values[1], conn_values[2])
                
                # Skip comment line
                i += 1
                # Next line contains: x, y, dx, dy
                i += 1
                coord_line = self.lines[i].strip()
                coord_values = re.findall(r'[\d\.\-]+E[\+\-]\d+', coord_line)
                if len(coord_values) >= 4:
                    self.data.element_coords[elem_id] = tuple(float(v) for v in coord_values[:4])
            i += 1
    
    def _parse_materials(self):
        """Parse material names and assignments."""
        # Find material names
        mat_names = []
        for line in self.lines:
            if line.strip().startswith('#'):
                match = re.match(r'#\s*(\d+)\s*-\s*(\w+)', line.strip())
                if match:
                    mat_names.append((int(match.group(1)), match.group(2)))
        
        self.data.material_names = [name for _, name in sorted(mat_names)]
        
        # Find material assignments per region
        in_material_section = False
        materials = []
        
        for i, line in enumerate(self.lines):
            if 'medium number per region' in line:
                in_material_section = True
                continue
            if in_material_section:
                if '---' in line:
                    break
                value = line.strip()
                if value and value.isdigit():
                    materials.append(int(value))
        
        self.data.materials = materials
    
    def _parse_boundary_conditions(self):
        """Parse boundary condition settings."""
        for i, line in enumerate(self.lines):
            if 'boundaries conditions' in line:
                values_line = self.lines[i + 1].strip()
                values = [int(v.strip()) for v in values_line.split(',') if v.strip()]
                if len(values) >= 3:
                    self.data.bc_default = values[0]
                    self.data.bc_nbbcda = values[1]
                    self.data.bc_allsur = values[2]
                break
        
        for i, line in enumerate(self.lines):
            if line.strip().startswith('* albedo'):
                albedo_line = self.lines[i + 1].strip()
                try:
                    self.data.albedo = float(albedo_line)
                except ValueError:
                    pass
                break


class TrackingComparator:
    """Compare tracking data between different SALT methods."""
    
    def __init__(self, tdt_data: TDTDatData, 
                 moc_data: Optional[SALTTrackingData] = None,
                 cp_data: Optional[SALTTrackingData] = None,
                 ic_data: Optional[SALTTrackingData] = None):
        self.tdt = tdt_data
        self.moc = moc_data
        self.cp = cp_data
        self.ic = ic_data
        
    def compare_all(self) -> Dict:
        """Run all comparisons and return results."""
        results = {
            'summary': self._generate_summary(),
            'region_comparison': self._compare_regions(),
            'surface_comparison': self._compare_surfaces(),
            'volume_comparison': self._compare_volumes(),
            'material_comparison': self._compare_materials(),
            'connectivity_analysis': self._analyze_connectivity(),
            'discrepancies': self._find_discrepancies(),
        }
        return results
    
    def _generate_summary(self) -> Dict:
        """Generate summary of all tracking data."""
        summary = {
            'tdt_input': {
                'nodes': self.tdt.node,
                'elements': self.tdt.elem,
                'regions': self.tdt.nreg,
                'macros': self.tdt.macr,
                'materials': len(self.tdt.material_names),
            }
        }
        
        for name, data in [('moc', self.moc), ('cp', self.cp), ('ic', self.ic)]:
            if data:
                summary[name] = {
                    'title': data.title,
                    'type': data.tracking_type,
                    'nreg': data.nreg,
                    'nsurf': data.nsurf,
                    'method': data.method,
                    'merged_regions': data.merged_regions,
                    'merged_surfaces': data.merged_surfaces,
                    'nmacro': data.nmacro,
                    'ijat': data.ijat,
                    'rms_error': data.rms_error,
                    'max_error': data.max_error,
                    'avg_error': data.avg_error,
                    'num_volumes': len(data.volumes),
                    'num_matalb': len(data.matalb),
                    'num_icode': len(data.icode),
                }
        
        return summary
    
    def _compare_regions(self) -> Dict:
        """Compare region counts between methods."""
        comparison = {
            'tdt_nreg': self.tdt.nreg,
        }
        
        for name, data in [('moc', self.moc), ('cp', self.cp), ('ic', self.ic)]:
            if data:
                comparison[f'{name}_nreg'] = data.nreg
                comparison[f'{name}_merged_regions'] = data.merged_regions
                comparison[f'{name}_match_tdt'] = data.nreg == self.tdt.nreg
        
        return comparison
    
    def _compare_surfaces(self) -> Dict:
        """Compare surface counts between methods."""
        comparison = {}
        
        for name, data in [('moc', self.moc), ('cp', self.cp), ('ic', self.ic)]:
            if data:
                comparison[f'{name}_nsurf'] = data.nsurf
                comparison[f'{name}_merged_surfaces'] = data.merged_surfaces
                comparison[f'{name}_icode_count'] = len(data.icode)
        
        return comparison
    
    def _compare_volumes(self) -> Dict:
        """Compare volume arrays between methods."""
        comparison = {}
        
        datasets = []
        for name, data in [('moc', self.moc), ('cp', self.cp), ('ic', self.ic)]:
            if data and data.volumes:
                comparison[f'{name}_volume_count'] = len(data.volumes)
                comparison[f'{name}_total_volume'] = sum(data.volumes)
                comparison[f'{name}_nonzero_volumes'] = sum(1 for v in data.volumes if v > 0)
                datasets.append((name, data.volumes))
        
        # Compare pairwise
        if len(datasets) >= 2:
            for i in range(len(datasets)):
                for j in range(i + 1, len(datasets)):
                    name1, vol1 = datasets[i]
                    name2, vol2 = datasets[j]
                    
                    # Check if arrays match
                    min_len = min(len(vol1), len(vol2))
                    if min_len > 0:
                        diff = [abs(vol1[k] - vol2[k]) for k in range(min_len)]
                        comparison[f'{name1}_vs_{name2}_max_diff'] = max(diff)
                        comparison[f'{name1}_vs_{name2}_volumes_match'] = max(diff) < 1e-10
        
        return comparison
    
    def _compare_materials(self) -> Dict:
        """Compare material assignments."""
        comparison = {
            'tdt_materials': self.tdt.materials,
            'tdt_material_names': self.tdt.material_names,
            'tdt_material_count': len(self.tdt.materials),
        }
        
        for name, data in [('moc', self.moc), ('cp', self.cp), ('ic', self.ic)]:
            if data:
                comparison[f'{name}_matalb'] = data.matalb
                comparison[f'{name}_nbmix'] = data.nbmix
                
                # Count positive materials (actual regions, not boundaries)
                pos_matalb = [m for m in data.matalb if m > 0]
                comparison[f'{name}_positive_matalb_count'] = len(pos_matalb)
                
                # Check if TDT materials match positive MATALB
                if pos_matalb and self.tdt.materials:
                    comparison[f'{name}_materials_match'] = pos_matalb == self.tdt.materials
        
        return comparison
    
    def _analyze_connectivity(self) -> Dict:
        """Analyze element connectivity from TDT file."""
        analysis = {
            'total_elements': len(self.tdt.elements),
            'boundary_elements': 0,  # Elements connected to 0
            'internal_elements': 0,
        }
        
        boundary_elements = []
        for elem_id, (etype, n1, n2) in self.tdt.elements.items():
            if n1 == 0 or n2 == 0:
                analysis['boundary_elements'] += 1
                boundary_elements.append(elem_id)
            else:
                analysis['internal_elements'] += 1
        
        analysis['boundary_element_ids'] = boundary_elements
        
        # Count unique regions connected
        connected_regions = set()
        for elem_id, (etype, n1, n2) in self.tdt.elements.items():
            if n1 > 0:
                connected_regions.add(n1)
            if n2 > 0:
                connected_regions.add(n2)
        
        analysis['connected_regions'] = sorted(connected_regions)
        analysis['num_connected_regions'] = len(connected_regions)
        
        return analysis
    
    def _find_discrepancies(self) -> List[str]:
        """Find discrepancies between tracking methods."""
        discrepancies = []
        
        # Check region count differences
        if self.moc and self.ic:
            if self.moc.nreg != self.ic.nreg:
                discrepancies.append(
                    f"Region count mismatch: MOC has {self.moc.nreg}, IC has {self.ic.nreg}"
                )
        
        if self.moc and self.cp:
            if self.moc.nreg != self.cp.nreg:
                discrepancies.append(
                    f"Region count mismatch: MOC has {self.moc.nreg}, CP has {self.cp.nreg}"
                )
        
        # Check surface count differences
        if self.moc and self.ic:
            if self.moc.nsurf != self.ic.nsurf:
                discrepancies.append(
                    f"Surface count mismatch: MOC has {self.moc.nsurf} (ICODE: {len(self.moc.icode)}), "
                    f"IC has {self.ic.nsurf} (ICODE: {len(self.ic.icode)})"
                )
        
        # Check volume array sizes
        if self.moc and self.ic:
            if len(self.moc.volumes) != len(self.ic.volumes):
                discrepancies.append(
                    f"Volume array size mismatch: MOC has {len(self.moc.volumes)}, IC has {len(self.ic.volumes)}"
                )
        
        # Check MATALB differences
        if self.moc and self.ic:
            if len(self.moc.matalb) != len(self.ic.matalb):
                discrepancies.append(
                    f"MATALB size mismatch: MOC has {len(self.moc.matalb)}, IC has {len(self.ic.matalb)}"
                )
            else:
                diffs = [(i, self.moc.matalb[i], self.ic.matalb[i]) 
                         for i in range(len(self.moc.matalb)) 
                         if self.moc.matalb[i] != self.ic.matalb[i]]
                if diffs:
                    discrepancies.append(
                        f"MATALB value differences at indices: {diffs[:10]}..."
                    )
        
        # Check method differences
        if self.moc and self.ic:
            discrepancies.append(
                f"Method difference: MOC uses METHOD={self.moc.method}, IC uses METHOD={self.ic.method}"
            )
        
        # Check NMACRO
        if self.moc and self.ic:
            if self.moc.nmacro != self.ic.nmacro:
                discrepancies.append(
                    f"NMACRO difference: MOC has {self.moc.nmacro}, IC has {self.ic.nmacro}"
                )
        
        # Check IJAT (interface current components)
        if self.moc and self.ic:
            if self.moc.ijat != self.ic.ijat:
                discrepancies.append(
                    f"IJAT difference: MOC has {self.moc.ijat}, IC has {self.ic.ijat}"
                )
        
        return discrepancies
    
    def print_report(self):
        """Print a comprehensive comparison report."""
        results = self.compare_all()
        
        print("=" * 80)
        print("SALT TRACKING COMPARISON REPORT")
        print("=" * 80)
        
        # Summary
        print("\n" + "-" * 40)
        print("SUMMARY")
        print("-" * 40)
        
        summary = results['summary']
        
        print(f"\nTDT Input File:")
        for key, value in summary.get('tdt_input', {}).items():
            print(f"  {key}: {value}")
        
        for method in ['moc', 'cp', 'ic']:
            if method in summary:
                print(f"\n{method.upper()} Tracking:")
                for key, value in summary[method].items():
                    print(f"  {key}: {value}")
        
        # Region comparison
        print("\n" + "-" * 40)
        print("REGION COMPARISON")
        print("-" * 40)
        for key, value in results['region_comparison'].items():
            print(f"  {key}: {value}")
        
        # Surface comparison
        print("\n" + "-" * 40)
        print("SURFACE COMPARISON")
        print("-" * 40)
        for key, value in results['surface_comparison'].items():
            print(f"  {key}: {value}")
        
        # Volume comparison
        print("\n" + "-" * 40)
        print("VOLUME COMPARISON")
        print("-" * 40)
        for key, value in results['volume_comparison'].items():
            if not isinstance(value, (list, dict)):
                print(f"  {key}: {value}")
        
        # Connectivity analysis
        print("\n" + "-" * 40)
        print("CONNECTIVITY ANALYSIS (from TDT)")
        print("-" * 40)
        conn = results['connectivity_analysis']
        print(f"  Total elements: {conn['total_elements']}")
        print(f"  Boundary elements: {conn['boundary_elements']}")
        print(f"  Internal elements: {conn['internal_elements']}")
        print(f"  Connected regions: {conn['num_connected_regions']}")
        
        # Discrepancies
        print("\n" + "-" * 40)
        print("DISCREPANCIES FOUND")
        print("-" * 40)
        for disc in results['discrepancies']:
            print(f"  ⚠ {disc}")
        
        if not results['discrepancies']:
            print("  ✓ No discrepancies found")
        
        print("\n" + "=" * 80)
        
        return results


def analyze_volume_distribution(salt_data: SALTTrackingData, tdt_data: TDTDatData):
    """Analyze and compare volume distributions."""
    print("\n" + "-" * 40)
    print(f"VOLUME DISTRIBUTION ANALYSIS ({salt_data.tracking_type})")
    print("-" * 40)
    
    volumes = salt_data.volumes
    matalb = salt_data.matalb
    
    # Group volumes by material
    material_volumes = {}
    for i, (vol, mat) in enumerate(zip(volumes, matalb)):
        if mat not in material_volumes:
            material_volumes[mat] = {'total': 0, 'count': 0, 'indices': []}
        material_volumes[mat]['total'] += vol
        material_volumes[mat]['count'] += 1
        material_volumes[mat]['indices'].append(i)
    
    print("\nVolumes grouped by material (MATALB):")
    for mat in sorted(material_volumes.keys()):
        info = material_volumes[mat]
        mat_name = ""
        if mat > 0 and mat <= len(tdt_data.material_names):
            mat_name = f" ({tdt_data.material_names[mat-1]})"
        print(f"  Material {mat:3d}{mat_name}: "
              f"Total={info['total']:.6f}, Count={info['count']}, "
              f"Indices={info['indices'][:5]}{'...' if len(info['indices']) > 5 else ''}")
    
    return material_volumes


def main():
    """Main function to run tracking comparison."""
    # Define paths
    base_path = Path(__file__).parent
    salt_output_path = base_path / "SALT_tracking_output"
    tdt_path = base_path.parent.parent / "tdt_data" / "AT10_BOX_TISO.dat"
    
    # Parse TDT input file
    print("Parsing TDT input file...")
    tdt_parser = TDTDatParser(str(tdt_path))
    tdt_data = tdt_parser.parse()
    
    # Parse SALT output files
    moc_data = None
    cp_data = None
    ic_data = None
    
    moc_file = salt_output_path / "SALT_MOC_BOX.out"
    cp_file = salt_output_path / "SALT_CP_BOX.out"
    ic_file = salt_output_path / "SALT_IC_BOX.out"
    
    if moc_file.exists():
        print("Parsing MOC tracking output...")
        moc_parser = SALTOutputParser(str(moc_file))
        moc_data = moc_parser.parse()
    
    if cp_file.exists():
        print("Parsing CP tracking output...")
        cp_parser = SALTOutputParser(str(cp_file))
        cp_data = cp_parser.parse()
    
    if ic_file.exists():
        print("Parsing IC (multicell) tracking output...")
        ic_parser = SALTOutputParser(str(ic_file))
        ic_data = ic_parser.parse()
    
    # Run comparison
    comparator = TrackingComparator(tdt_data, moc_data, cp_data, ic_data)
    results = comparator.print_report()
    
    # Detailed volume analysis
    if moc_data:
        analyze_volume_distribution(moc_data, tdt_data)
    if ic_data:
        analyze_volume_distribution(ic_data, tdt_data)
    
    # Additional IC-specific analysis
    if ic_data:
        print("\n" + "-" * 40)
        print("IC METHOD SPECIFIC ANALYSIS")
        print("-" * 40)
        print(f"  MACRO flux count: {ic_data.macro_flux_count}")
        print(f"  Perimeter elements: {len(ic_data.perimeter_elements)}")
        print(f"  IJAT (interface currents): {ic_data.ijat}")
        print(f"  NMIX (perimeter elements): {ic_data.nmix}")
        
        # The IC method reports 48 regions in macro but 49 total
        # This might be the source of the discrepancy
        if ic_data.macro_flux_count != ic_data.nreg:
            print(f"\n  ⚠ POTENTIAL ISSUE:")
            print(f"    Macro flux count ({ic_data.macro_flux_count}) != NREG ({ic_data.nreg})")
            print(f"    This suggests the IC method treats one region differently (possibly void/boundary)")
    
    # Compare KEYMRG arrays
    print("\n" + "-" * 40)
    print("KEYMRG (Key Merge) COMPARISON")
    print("-" * 40)
    
    if moc_data and ic_data:
        print(f"\nMOC KEYMRG ({len(moc_data.keymrg)} entries):")
        print(f"  Range: {min(moc_data.keymrg)} to {max(moc_data.keymrg)}")
        print(f"  Negative (surfaces): {sum(1 for k in moc_data.keymrg if k < 0)}")
        print(f"  Zero: {sum(1 for k in moc_data.keymrg if k == 0)}")
        print(f"  Positive (regions): {sum(1 for k in moc_data.keymrg if k > 0)}")
        
        print(f"\nIC KEYMRG ({len(ic_data.keymrg)} entries):")
        print(f"  Range: {min(ic_data.keymrg)} to {max(ic_data.keymrg)}")
        print(f"  Negative (surfaces): {sum(1 for k in ic_data.keymrg if k < 0)}")
        print(f"  Zero: {sum(1 for k in ic_data.keymrg if k == 0)}")
        print(f"  Positive (regions): {sum(1 for k in ic_data.keymrg if k > 0)}")
        
        # Check for specific differences
        if len(moc_data.keymrg) != len(ic_data.keymrg):
            print(f"\n  ⚠ KEYMRG length differs: MOC={len(moc_data.keymrg)}, IC={len(ic_data.keymrg)}")
            extra_in_ic = len(ic_data.keymrg) - len(moc_data.keymrg)
            print(f"    IC has {extra_in_ic} extra entries")
    
    # Detailed volume-by-volume comparison for positive materials
    if moc_data and ic_data:
        print("\n" + "-" * 40)
        print("DETAILED VOLUME COMPARISON (Positive Materials Only)")
        print("-" * 40)
        
        # Extract volumes for positive materials (actual regions)
        moc_positive = [(i, v, m) for i, (v, m) in enumerate(zip(moc_data.volumes, moc_data.matalb)) if m > 0]
        ic_positive = [(i, v, m) for i, (v, m) in enumerate(zip(ic_data.volumes, ic_data.matalb)) if m > 0]
        
        print(f"\nMOC positive material regions: {len(moc_positive)}")
        print(f"IC positive material regions: {len(ic_positive)}")
        
        # Group by material and compare
        print("\nMaterial-wise volume totals:")
        for mat in [1, 2, 3]:
            moc_mat_vol = sum(v for _, v, m in moc_positive if m == mat)
            ic_mat_vol = sum(v for _, v, m in ic_positive if m == mat)
            mat_name = tdt_data.material_names[mat-1] if mat <= len(tdt_data.material_names) else f"Material {mat}"
            diff = moc_mat_vol - ic_mat_vol
            print(f"  {mat_name}:")
            print(f"    MOC: {moc_mat_vol:.6f}")
            print(f"    IC:  {ic_mat_vol:.6f}")
            print(f"    Diff: {diff:.6f} ({diff/moc_mat_vol*100:.2f}%)" if moc_mat_vol > 0 else "    Diff: N/A")
        
        # Find the missing region
        print("\n" + "-" * 40)
        print("MISSING REGION ANALYSIS")
        print("-" * 40)
        
        # Compare individual volumes
        moc_vols_sorted = sorted([v for _, v, m in moc_positive if m > 0], reverse=True)
        ic_vols_sorted = sorted([v for _, v, m in ic_positive if m > 0], reverse=True)
        
        print(f"\nMOC unique volume values: {len(set(moc_vols_sorted))}")
        print(f"IC unique volume values: {len(set(ic_vols_sorted))}")
        
        # Find volumes present in MOC but not in IC
        moc_vol_counts = {}
        for v in moc_vols_sorted:
            v_rounded = round(v, 6)
            moc_vol_counts[v_rounded] = moc_vol_counts.get(v_rounded, 0) + 1
        
        ic_vol_counts = {}
        for v in ic_vols_sorted:
            v_rounded = round(v, 6)
            ic_vol_counts[v_rounded] = ic_vol_counts.get(v_rounded, 0) + 1
        
        print("\nVolume count comparison (volumes that differ):")
        all_vols = set(moc_vol_counts.keys()) | set(ic_vol_counts.keys())
        for vol in sorted(all_vols, reverse=True):
            moc_count = moc_vol_counts.get(vol, 0)
            ic_count = ic_vol_counts.get(vol, 0)
            if moc_count != ic_count:
                print(f"  Volume {vol}: MOC has {moc_count}, IC has {ic_count} (diff: {moc_count - ic_count})")
        
        # Identify which specific region is missing
        print("\n" + "-" * 40)
        print("SURFACE/BOUNDARY ANALYSIS")
        print("-" * 40)
        
        # MOC uses 6 ICODEs, IC uses 8 ICODEs
        print(f"\nMOC ICODE: {moc_data.icode}")
        print(f"IC ICODE:  {ic_data.icode}")
        
        # Analyze negative MATALB (boundary/surface markers)
        moc_neg_matalb = sorted(set(m for m in moc_data.matalb if m < 0))
        ic_neg_matalb = sorted(set(m for m in ic_data.matalb if m < 0))
        
        print(f"\nMOC negative MATALB values: {moc_neg_matalb}")
        print(f"IC negative MATALB values: {ic_neg_matalb}")
        
        # The key insight: IC has 4 extra boundary types (-8,-7,-6,-5)
        # These represent the 4 corners of the perimeter in the macro geometry
        extra_boundaries = set(ic_neg_matalb) - set(moc_neg_matalb)
        if extra_boundaries:
            print(f"\n  ⚠ IC has additional boundary types: {sorted(extra_boundaries)}")
            print("    This indicates the IC method subdivides boundaries differently")
        
        # Check the void region (MATALB = 0)
        moc_void = [(i, v) for i, (v, m) in enumerate(zip(moc_data.volumes, moc_data.matalb)) if m == 0]
        ic_void = [(i, v) for i, (v, m) in enumerate(zip(ic_data.volumes, ic_data.matalb)) if m == 0]
        
        print(f"\nVoid regions (MATALB=0):")
        print(f"  MOC: {moc_void}")
        print(f"  IC:  {ic_void}")
    
    # Calculate and display total geometry volume
    print("\n" + "-" * 40)
    print("GEOMETRY VOLUME CHECK")
    print("-" * 40)
    
    # From BOX_TEST.py: bounding_box_length = 3.85 (guessed from typical AT10 dimensions)
    # Calculate expected total volume
    if moc_data and tdt_data:
        moc_actual_vol = sum(v for v, m in zip(moc_data.volumes, moc_data.matalb) if m > 0)
        ic_actual_vol = sum(v for v, m in zip(ic_data.volumes, ic_data.matalb) if m > 0) if ic_data else 0
        
        print(f"\nTotal volume of positive material regions:")
        print(f"  MOC: {moc_actual_vol:.6f}")
        print(f"  IC:  {ic_actual_vol:.6f}")
        print(f"  Difference: {moc_actual_vol - ic_actual_vol:.6f}")
        
        # The difference should be approximately one region's volume
        if abs(moc_actual_vol - ic_actual_vol) > 1e-6:
            missing_vol = moc_actual_vol - ic_actual_vol
            print(f"\n  ⚠ MISSING VOLUME: {missing_vol:.6f}")
            print(f"    This corresponds to ~{abs(missing_vol/1.677025):.1f} central moderator region(s)")
    
    # Print conclusions
    print_conclusions(moc_data, cp_data, ic_data, tdt_data)
    
    return results


def print_conclusions(moc_data, cp_data, ic_data, tdt_data):
    """Print conclusions and recommendations based on the analysis."""
    print("\n" + "=" * 80)
    print("CONCLUSIONS AND ROOT CAUSE ANALYSIS")
    print("=" * 80)
    
    print("""
KEY FINDINGS:
-------------

1. REGION COUNT DISCREPANCY:
   - MOC/CP: 49 merged regions (matches TDT input)
   - IC: 48 merged regions in MACRO, but reports NREG=49
   - The IC method is MISSING ONE REGION (the central MODERATOR region with volume 1.677025)

2. SURFACE/BOUNDARY HANDLING:
   - MOC/CP: 28 surfaces with 6 ICODE types (simple boundary treatment)
   - IC: 32 surfaces with 8 ICODE types (macro geometry creates additional perimeter surfaces)
   - IC adds 4 corner perimeter surfaces for the MACRO geometry

3. VOLUME ARRAY STRUCTURE:
   - MOC/CP: 78 entries = 28 surfaces + 1 void + 49 regions
   - IC: 81 entries = 32 surfaces + 1 void + 48 regions (confirms missing region)

4. ROOT CAUSE:
   - The IC (Interface Current / Multicell) method creates a MACRO geometry wrapper
   - The MACRO geometry has its own perimeter (32 elements as reported in NMIX)
   - During this process, ONE CENTRAL MODERATOR REGION (index 29 in MOC, volume=1.677025)
     is NOT being included in the IC tracking
   - This is the largest moderator volume and likely represents the center of the geometry

5. TECHNICAL DETAILS:
   - KEYMRG shows MOC has regions 1-49, IC only has 1-48
   - The missing region has MATALB=1 (MODERATOR material)
   - IC method uses METHOD=5 (multicell surfacic), MOC uses METHOD=4 (PIJ/MOC)

POTENTIAL CAUSES:
-----------------
a) The central region may be treated as part of the MACRO boundary rather than an interior region
b) The geometry description may need adjustment for IC method compatibility
c) There may be a bug in how SALT handles the central void/moderator region in IC mode

RECOMMENDATIONS:
----------------
1. Check if the central moderator region (node 29/30 area) has correct connectivity in .dat file
2. Verify that the MACRO geometry definition includes all interior regions
3. Consider if the IC method requires different geometry specifications
4. The MOC/CP results appear correct - use those for production calculations
""")


def compare_glow_vs_geo():
    """Compare GLOW-generated geometry with GEO-generated geometry to identify root cause."""
    print("\n" + "=" * 80)
    print("GLOW vs GEO COMPARISON")
    print("=" * 80)
    
    base_path = Path(__file__).parent
    salt_output_path = base_path / "SALT_tracking_output"
    geo_tdt_path = base_path / "GEO_G2S_tdt_data" / "AT10_BOX_TISO_GEO.dat"
    glow_tdt_path = base_path.parent.parent / "tdt_data" / "AT10_BOX_TISO.dat"
    
    # Parse GLOW IC output
    glow_ic_file = salt_output_path / "glow_SALT_IC_BOX.out"
    geo_ic_file = salt_output_path / "geo_g2s_SALT_IC_BOX.out"
    
    glow_ic_data = None
    geo_ic_data = None
    
    if glow_ic_file.exists():
        print("\nParsing GLOW IC tracking output...")
        glow_ic_parser = SALTOutputParser(str(glow_ic_file))
        glow_ic_data = glow_ic_parser.parse()
    
    if geo_ic_file.exists():
        print("Parsing GEO IC tracking output...")
        geo_ic_parser = SALTOutputParser(str(geo_ic_file))
        geo_ic_data = geo_ic_parser.parse()
    
    if not glow_ic_data or not geo_ic_data:
        print("ERROR: Could not load both IC output files")
        return
    
    print("\n" + "-" * 60)
    print("IC METHOD COMPARISON: GLOW vs GEO")
    print("-" * 60)
    
    # Key metrics comparison
    comparison_table = [
        ("Title", glow_ic_data.title, geo_ic_data.title),
        ("NREG (total regions)", glow_ic_data.nreg, geo_ic_data.nreg),
        ("Merged regions", glow_ic_data.merged_regions, geo_ic_data.merged_regions),
        ("Merged surfaces", glow_ic_data.merged_surfaces, geo_ic_data.merged_surfaces),
        ("MACRO flux count", glow_ic_data.macro_flux_count, geo_ic_data.macro_flux_count),
        ("IJAT (interface currents)", glow_ic_data.ijat, geo_ic_data.ijat),
        ("NMIX (perimeter elements)", glow_ic_data.nmix, geo_ic_data.nmix),
        ("Volume array size", len(glow_ic_data.volumes), len(geo_ic_data.volumes)),
        ("MATALB array size", len(glow_ic_data.matalb), len(geo_ic_data.matalb)),
        ("KEYMRG array size", len(glow_ic_data.keymrg), len(geo_ic_data.keymrg)),
        ("ICODE count", len(glow_ic_data.icode), len(geo_ic_data.icode)),
        ("NBMIX", glow_ic_data.nbmix, geo_ic_data.nbmix),
        ("RMS error (%)", f"{glow_ic_data.rms_error:.5f}", f"{geo_ic_data.rms_error:.5f}"),
    ]
    
    print(f"\n{'Metric':<30} {'GLOW':<20} {'GEO':<20} {'Match':<10}")
    print("-" * 80)
    for metric, glow_val, geo_val in comparison_table:
        match = "✓" if str(glow_val) == str(geo_val) else "✗"
        print(f"{metric:<30} {str(glow_val):<20} {str(geo_val):<20} {match:<10}")
    
    # Critical difference analysis
    print("\n" + "-" * 60)
    print("CRITICAL DIFFERENCES")
    print("-" * 60)
    
    if glow_ic_data.merged_regions != geo_ic_data.merged_regions:
        diff = geo_ic_data.merged_regions - glow_ic_data.merged_regions
        print(f"\n⚠ MERGED REGIONS: GEO has {diff} more region(s) than GLOW")
        print(f"  GLOW: {glow_ic_data.merged_regions} merged regions")
        print(f"  GEO:  {geo_ic_data.merged_regions} merged regions")
    
    if glow_ic_data.macro_flux_count != geo_ic_data.macro_flux_count:
        diff = geo_ic_data.macro_flux_count - glow_ic_data.macro_flux_count
        print(f"\n⚠ MACRO FLUX COUNT: GEO has {diff} more flux region(s)")
        print(f"  GLOW: {glow_ic_data.macro_flux_count} flux regions in macro")
        print(f"  GEO:  {geo_ic_data.macro_flux_count} flux regions in macro")
    
    if glow_ic_data.ijat != geo_ic_data.ijat:
        print(f"\n⚠ IJAT (Interface Currents): Different perimeter treatment")
        print(f"  GLOW: {glow_ic_data.ijat} interface currents")
        print(f"  GEO:  {geo_ic_data.ijat} interface currents")
    
    # Volume comparison
    print("\n" + "-" * 60)
    print("VOLUME ANALYSIS")
    print("-" * 60)
    
    glow_positive = [(i, v, m) for i, (v, m) in enumerate(zip(glow_ic_data.volumes, glow_ic_data.matalb)) if m > 0]
    geo_positive = [(i, v, m) for i, (v, m) in enumerate(zip(geo_ic_data.volumes, geo_ic_data.matalb)) if m > 0]
    
    glow_total = sum(v for _, v, _ in glow_positive)
    geo_total = sum(v for _, v, _ in geo_positive)
    
    print(f"\nGLOW positive material regions: {len(glow_positive)} (total vol: {glow_total:.6f})")
    print(f"GEO positive material regions:  {len(geo_positive)} (total vol: {geo_total:.6f})")
    print(f"Volume difference: {geo_total - glow_total:.6f}")
    
    # Check for the 1.677025 volume (central moderator)
    central_vol = 1.677025
    glow_has_central = any(abs(v - central_vol) < 0.001 for _, v, _ in glow_positive)
    geo_has_central = any(abs(v - central_vol) < 0.001 for _, v, _ in geo_positive)
    
    print(f"\nCentral moderator region (vol={central_vol}):")
    print(f"  GLOW: {'Present' if glow_has_central else 'MISSING!'}")
    print(f"  GEO:  {'Present' if geo_has_central else 'MISSING!'}")
    
    # KEYMRG comparison
    print("\n" + "-" * 60)
    print("KEYMRG COMPARISON")
    print("-" * 60)
    
    glow_pos_keymrg = max(glow_ic_data.keymrg) if glow_ic_data.keymrg else 0
    geo_pos_keymrg = max(geo_ic_data.keymrg) if geo_ic_data.keymrg else 0
    
    print(f"\nGLOW KEYMRG max positive: {glow_pos_keymrg}")
    print(f"GEO KEYMRG max positive:  {geo_pos_keymrg}")
    
    # ICODE comparison
    print("\n" + "-" * 60)
    print("BOUNDARY CONDITIONS (ICODE)")
    print("-" * 60)
    print(f"\nGLOW ICODE: {glow_ic_data.icode}")
    print(f"GEO ICODE:  {geo_ic_data.icode}")
    
    # Negative MATALB (boundary markers)
    glow_neg = sorted(set(m for m in glow_ic_data.matalb if m < 0))
    geo_neg = sorted(set(m for m in geo_ic_data.matalb if m < 0))
    
    print(f"\nGLOW boundary markers: {glow_neg}")
    print(f"GEO boundary markers:  {geo_neg}")
    
    # Element ordering analysis
    print("\n" + "-" * 60)
    print("ROOT CAUSE ANALYSIS")
    print("-" * 60)
    
    print("""
FINDINGS:
---------
1. GEO-generated geometry: IC method correctly identifies 49 regions
2. GLOW-generated geometry: IC method only identifies 48 regions (missing 1)

3. The central moderator region (volume 1.677025) is:
   - PRESENT in GEO IC tracking
   - MISSING in GLOW IC tracking

4. Key structural differences:
   - GLOW IC has 32 surfaces, 8 ICODEs, 32 IJAT
   - GEO IC has 28 surfaces, 4 ICODEs, 28 IJAT
   
5. This indicates the GLOW .dat file creates additional perimeter complexity
   that causes SALT IC to lose track of the central region.

DIAGNOSIS:
----------
The issue is NOT in the SALT procedure itself (GEO works correctly).
The issue is in the GLOW-generated TDT file structure.

Specific problems in GLOW .dat file:
a) Element ordering/connectivity differs from GEO format
b) Boundary element definitions create ambiguous perimeter
c) The IC method interprets GLOW's connectivity as having 8 boundary types
   instead of 4, causing it to create extra perimeter elements and lose
   an interior region
""")
    
    return glow_ic_data, geo_ic_data


def analyze_tdt_connectivity(glow_tdt_path, geo_tdt_path):
    """Analyze and compare TDT file connectivity."""
    print("\n" + "=" * 80)
    print("TDT FILE CONNECTIVITY ANALYSIS")
    print("=" * 80)
    
    # Parse both TDT files
    glow_parser = TDTDatParser(str(glow_tdt_path))
    glow_data = glow_parser.parse()
    
    geo_parser = TDTDatParser(str(geo_tdt_path))
    geo_data = geo_parser.parse()
    
    print(f"\nGLOW TDT: {len(glow_data.elements)} elements, {glow_data.node} nodes")
    print(f"GEO TDT:  {len(geo_data.elements)} elements, {geo_data.node} nodes")
    
    # Analyze boundary surfaces (node 0 connections)
    analyze_outer_surfaces(glow_data, "GLOW")
    analyze_outer_surfaces(geo_data, "GEO")
    
    # Count boundary elements (those connected to node 0)
    glow_boundary = sum(1 for e in glow_data.elements.values() if e[1] == 0 or e[2] == 0)
    geo_boundary = sum(1 for e in geo_data.elements.values() if e[1] == 0 or e[2] == 0)
    
    print(f"\nTotal boundary elements (connected to node 0):")
    print(f"  GLOW: {glow_boundary}")
    print(f"  GEO:  {geo_boundary}")
    
    # Analyze boundary element ordering
    print("\n" + "-" * 40)
    print("BOUNDARY ELEMENT ORDERING ANALYSIS")
    print("-" * 40)
    
    # Get boundary element IDs and their order
    glow_boundary_elems = [(elem_id, etype, n1, n2) for elem_id, (etype, n1, n2) in glow_data.elements.items() if n1 == 0 or n2 == 0]
    geo_boundary_elems = [(elem_id, etype, n1, n2) for elem_id, (etype, n1, n2) in geo_data.elements.items() if n1 == 0 or n2 == 0]
    
    # Sort by element ID
    glow_boundary_elems.sort(key=lambda x: x[0])
    geo_boundary_elems.sort(key=lambda x: x[0])
    
    print("\nGLOW boundary elements (first 10):")
    for i, (elem_id, etype, n1, n2) in enumerate(glow_boundary_elems[:10]):
        print(f"  Elem {elem_id}: type={etype}, nodes=({n1}, {n2})")
    
    print("\nGEO boundary elements (first 10):")
    for i, (elem_id, etype, n1, n2) in enumerate(geo_boundary_elems[:10]):
        print(f"  Elem {elem_id}: type={etype}, nodes=({n1}, {n2})")
    
    # Check if boundary elements are grouped by side
    print("\n" + "-" * 40)
    print("BOUNDARY ELEMENT GROUPING")
    print("-" * 40)
    
    def analyze_boundary_grouping(boundary_elems, coords, name):
        """Analyze how boundary elements are grouped/ordered."""
        print(f"\n{name} boundary element analysis:")
        
        # Count sequential vs scattered boundary elements
        boundary_ids = sorted([e[0] for e in boundary_elems])
        gaps = []
        for i in range(1, len(boundary_ids)):
            gap = boundary_ids[i] - boundary_ids[i-1]
            if gap > 1:
                gaps.append((boundary_ids[i-1], boundary_ids[i], gap))
        
        print(f"  Boundary element ID range: {min(boundary_ids)} to {max(boundary_ids)}")
        print(f"  Number of gaps in sequence: {len(gaps)}")
        if gaps:
            print(f"  Gaps: {gaps[:5]}{'...' if len(gaps) > 5 else ''}")
        
        return boundary_ids
    
    glow_bd_ids = analyze_boundary_grouping(glow_boundary_elems, glow_data.element_coords, "GLOW")
    geo_bd_ids = analyze_boundary_grouping(geo_boundary_elems, geo_data.element_coords, "GEO")
    
    # Count elements per node
    glow_node_elem_count = {}
    for elem_id, (etype, n1, n2) in glow_data.elements.items():
        if n1 > 0:
            glow_node_elem_count[n1] = glow_node_elem_count.get(n1, 0) + 1
        if n2 > 0:
            glow_node_elem_count[n2] = glow_node_elem_count.get(n2, 0) + 1
    
    geo_node_elem_count = {}
    for elem_id, (etype, n1, n2) in geo_data.elements.items():
        if n1 > 0:
            geo_node_elem_count[n1] = geo_node_elem_count.get(n1, 0) + 1
        if n2 > 0:
            geo_node_elem_count[n2] = geo_node_elem_count.get(n2, 0) + 1
    
    print("\n" + "-" * 40)
    print("Node connectivity distribution:")
    print("-" * 40)
    
    for count in sorted(set(glow_node_elem_count.values())):
        glow_nodes = sum(1 for c in glow_node_elem_count.values() if c == count)
        geo_nodes = sum(1 for c in geo_node_elem_count.values() if c == count)
        print(f"  Nodes with {count} elements: GLOW={glow_nodes}, GEO={geo_nodes}")
    
    # Critical: Check flux region mapping differences
    print("\n" + "-" * 40)
    print("FLUX REGION MAPPING COMPARISON")
    print("-" * 40)
    
    print(f"\nGLOW flux mapping: {glow_data.flux_region_mapping[:20]}...")
    print(f"GEO flux mapping:  {geo_data.flux_region_mapping[:20]}...")
    
    # Check if mappings differ
    if glow_data.flux_region_mapping != geo_data.flux_region_mapping:
        print("\n⚠ Flux region mappings DIFFER!")
        
        # Find differences
        max_len = max(len(glow_data.flux_region_mapping), len(geo_data.flux_region_mapping))
        glow_set = set(glow_data.flux_region_mapping)
        geo_set = set(geo_data.flux_region_mapping)
        
        print(f"  GLOW unique flux regions: {sorted(glow_set)}")
        print(f"  GEO unique flux regions:  {sorted(geo_set)}")
        print(f"  In GEO but not GLOW: {sorted(geo_set - glow_set)}")
        print(f"  In GLOW but not GEO: {sorted(glow_set - geo_set)}")
    else:
        print("\n✓ Flux region mappings are IDENTICAL")
    
    return glow_data, geo_data


def analyze_outer_surfaces(tdt_data: TDTDatData, name: str):
    """
    Analyze the outer surfaces (elements connected to node 0) in a TDT geometry.
    
    In TDT format, elements are specified as:
        *type    node-   node+
    
    Node 0 is the special "outside" node. Any element with node- = 0 or node+ = 0
    is a boundary element that connects to the exterior.
    
    For a simple rectangular geometry with 7 segments per side, we expect 
    exactly 28 outer surface elements (7 × 4 sides).
    
    If we find MORE than 28, it means some interior elements are incorrectly
    connected to node 0 (e.g., the central moderator region).
    """
    print("\n" + "=" * 60)
    print(f"OUTER SURFACE ANALYSIS: {name}")
    print("=" * 60)
    
    # Collect all boundary elements (connected to node 0)
    boundary_elements = []
    for elem_id, (etype, node_minus, node_plus) in tdt_data.elements.items():
        if node_minus == 0 or node_plus == 0:
            # Get coordinates if available
            coords = tdt_data.element_coords.get(elem_id, (None, None, None, None))
            boundary_elements.append({
                'elem_id': elem_id,
                'type': etype,
                'node_minus': node_minus,
                'node_plus': node_plus,
                'cx': coords[0],
                'cy': coords[1],
                'dx': coords[2],  # For lines: dx component (or R for arcs)
                'dy': coords[3],  # For lines: dy component (or theta1 for arcs)
            })
    
    print(f"\nTotal elements connected to node 0: {len(boundary_elements)}")
    print(f"Expected for 4-sided geometry with 7 segments/side: 28")
    
    if len(boundary_elements) != 28:
        print(f"\n⚠ DISCREPANCY: Found {len(boundary_elements)} instead of 28!")
        print(f"   Extra elements: {len(boundary_elements) - 28}")
    
    # Find the bounding box to identify TRUE outer boundary
    all_cx = [be['cx'] for be in boundary_elements if be['cx'] is not None]
    all_cy = [be['cy'] for be in boundary_elements if be['cy'] is not None]
    
    if all_cx and all_cy:
        min_cx, max_cx = min(all_cx), max(all_cx)
        min_cy, max_cy = min(all_cy), max(all_cy)
        
        print(f"\nBounding box of node-0 elements:")
        print(f"  X range: [{min_cx:.4f}, {max_cx:.4f}]")
        print(f"  Y range: [{min_cy:.4f}, {max_cy:.4f}]")
        
        # Classify elements as truly outer or potentially interior
        tolerance = 0.01
        outer_left = []    # cx ≈ min_cx
        outer_right = []   # cx ≈ max_cx  
        outer_bottom = []  # cy ≈ min_cy
        outer_top = []     # cy ≈ max_cy
        interior = []      # Not on any edge
        
        for be in boundary_elements:
            cx, cy = be['cx'], be['cy']
            dx, dy = be['dx'], be['dy']
            
            if cx is None or cy is None:
                continue
                
            is_on_left = abs(cx - min_cx) < tolerance
            is_on_right = abs(cx - max_cx) < tolerance
            is_on_bottom = abs(cy - min_cy) < tolerance
            is_on_top = abs(cy - max_cy) < tolerance
            
            # Determine if element direction matches expected for outer boundary
            # Left edge: vertical line at x=min, dx≠0
            # Right edge: vertical line at x=max, dx≠0  
            # Bottom edge: horizontal line at y=min, dy≠0
            # Top edge: horizontal line at y=max, dy≠0
            
            if is_on_left and abs(dy) > tolerance:  # Vertical on left edge
                outer_left.append(be)
            elif is_on_right and abs(dy) > tolerance:  # Vertical on right edge
                outer_right.append(be)
            elif is_on_bottom and abs(dx) > tolerance:  # Horizontal on bottom edge
                outer_bottom.append(be)
            elif is_on_top and abs(dx) > tolerance:  # Horizontal on top edge
                outer_top.append(be)
            else:
                # This element is connected to node 0 but NOT on outer boundary!
                interior.append(be)
        
        print(f"\nClassification of node-0 elements:")
        print(f"  Left edge (x={min_cx:.4f}):   {len(outer_left)} elements")
        print(f"  Right edge (x={max_cx:.4f}):  {len(outer_right)} elements")
        print(f"  Bottom edge (y={min_cy:.4f}): {len(outer_bottom)} elements")
        print(f"  Top edge (y={max_cy:.4f}):    {len(outer_top)} elements")
        print(f"  Total on outer boundary:      {len(outer_left) + len(outer_right) + len(outer_bottom) + len(outer_top)}")
        
        if interior:
            print(f"\n  ⚠ INTERIOR ELEMENTS INCORRECTLY CONNECTED TO NODE 0: {len(interior)}")
            print(f"\n  These elements are NOT on the outer boundary but connect to node 0:")
            print(f"  {'Elem':<6} {'Node-':<8} {'Node+':<8} {'cx':<12} {'cy':<12} {'dx':<12} {'dy':<12}")
            print(f"  {'-'*6} {'-'*8} {'-'*8} {'-'*12} {'-'*12} {'-'*12} {'-'*12}")
            for be in interior:
                cx = f"{be['cx']:.4f}" if be['cx'] is not None else "N/A"
                cy = f"{be['cy']:.4f}" if be['cy'] is not None else "N/A"
                dx = f"{be['dx']:.4f}" if be['dx'] is not None else "N/A"
                dy = f"{be['dy']:.4f}" if be['dy'] is not None else "N/A"
                print(f"  {be['elem_id']:<6} {be['node_minus']:<8} {be['node_plus']:<8} {cx:<12} {cy:<12} {dx:<12} {dy:<12}")
            
            print(f"\n  ROOT CAUSE IDENTIFIED:")
            print(f"  These {len(interior)} interior elements are connected to node 0,")
            print(f"  causing SALT IC to interpret them as additional boundary surfaces.")
            print(f"  This creates {len(interior)} extra ICODEs (8 instead of 4).")
        else:
            print(f"\n  ✓ All node-0 elements are correctly on the outer boundary.")
    
    # Also check: are there any elements where BOTH nodes are 0? (would be invalid)
    both_zero = [be for be in boundary_elements if be['node_minus'] == 0 and be['node_plus'] == 0]
    if both_zero:
        print(f"\n  ⚠ INVALID: {len(both_zero)} elements have BOTH nodes = 0!")
    
    return {
        'total_boundary': len(boundary_elements),
        'expected': 28,
        'extra': len(boundary_elements) - 28,
        'interior_elements': interior if 'interior' in dir() else [],
    }


def analyze_boundary_condition_definitions(glow_tdt_path: str, geo_tdt_path: str):
    """
    Compare the boundary condition definitions between GLOW and GEO TDT files.
    
    The key difference is in how boundary conditions are specified:
    - GEO: nbbcda = 4 (explicitly defines 4 boundary condition groups)
    - GLOW: nbbcda = 0 (no explicit boundary condition groups)
    
    This affects how SALT IC interprets the perimeter.
    """
    print("\n" + "=" * 80)
    print("BOUNDARY CONDITION DEFINITION ANALYSIS")
    print("=" * 80)
    
    # Read raw file contents to find boundary condition sections
    with open(glow_tdt_path, 'r') as f:
        glow_content = f.read()
    
    with open(geo_tdt_path, 'r') as f:
        geo_content = f.read()
    
    # Parse GLOW boundary conditions
    print("\n--- GLOW BOUNDARY CONDITIONS ---")
    glow_bc_match = re.search(r'boundaries conditions.*?\n\s*([\d,\s]+)', glow_content)
    if glow_bc_match:
        bc_values = [int(v.strip()) for v in glow_bc_match.group(1).split(',') if v.strip()]
        print(f"  defaul, nbbcda, allsur = {bc_values}")
        glow_nbbcda = bc_values[1] if len(bc_values) > 1 else 0
    else:
        glow_nbbcda = 0
        print("  Could not parse boundary conditions")
    
    # Parse GEO boundary conditions  
    print("\n--- GEO BOUNDARY CONDITIONS ---")
    geo_bc_match = re.search(r'\*defaul\s+nbbcda.*?\n\s*([\d\s]+)', geo_content)
    if geo_bc_match:
        bc_values = geo_bc_match.group(1).split()
        print(f"  defaul, nbbcda, allsur, divsur, ndivsur = {bc_values}")
        geo_nbbcda = int(bc_values[1]) if len(bc_values) > 1 else 0
    else:
        geo_nbbcda = 0
        print("  Could not parse boundary conditions")
    
    # Find explicit boundary condition groups in GEO
    bc_groups = re.findall(r'particular boundary condition number\s+(\d+).*?\*elems.*?\n\s*([\d\s]+)', geo_content, re.DOTALL)
    
    print(f"\n--- COMPARISON ---")
    print(f"  GLOW nbbcda (number of BC groups): {glow_nbbcda}")
    print(f"  GEO nbbcda (number of BC groups):  {geo_nbbcda}")
    
    if glow_nbbcda != geo_nbbcda:
        print(f"\n  ⚠ CRITICAL DIFFERENCE FOUND!")
        print(f"  GLOW defines {glow_nbbcda} explicit boundary condition groups")
        print(f"  GEO defines {geo_nbbcda} explicit boundary condition groups")
    
    if bc_groups:
        print(f"\n  GEO boundary condition groups:")
        for bc_num, elems in bc_groups:
            elem_list = [int(e) for e in elems.split()]
            print(f"    BC {bc_num}: {len(elem_list)} elements -> {elem_list}")
    
    print(f"""
================================================================================
                      ROOT CAUSE IDENTIFIED
================================================================================

The issue is in the BOUNDARY CONDITION DEFINITION, not the element ordering:

GLOW TDT file:
  - nbbcda = 0 (NO explicit boundary condition groups defined)
  - SALT must infer boundary groups from element connectivity
  - This inference creates 8 boundary codes instead of 4

GEO TDT file:
  - nbbcda = 4 (4 explicit boundary condition groups defined)
  - Each group explicitly lists which 7 elements belong to it:
    * BC 1: elements on one side (7 elements)
    * BC 2: elements on another side (7 elements)  
    * BC 3: elements on third side (7 elements)
    * BC 4: elements on fourth side (7 elements)
  - SALT uses these explicit definitions → 4 ICODEs

FIX REQUIRED:
  GLOW's TDT generator needs to:
  1. Set nbbcda = 4 (or appropriate number of sides)
  2. Explicitly define which boundary elements belong to each side
  3. Group the 28 boundary elements into 4 groups of 7

This is why SALT IC creates 32 perimeter surfaces (8 groups × ~4 elements)
instead of 28 (4 groups × 7 elements), losing the central moderator region.
================================================================================
""")
    
    return {
        'glow_nbbcda': glow_nbbcda,
        'geo_nbbcda': geo_nbbcda,
        'geo_bc_groups': bc_groups,
    }


def map_geo_to_glow_boundary_elements(geo_tdt_path: str, glow_tdt_path: str):
    """
    Map boundary elements from GEO TDT file to their corresponding elements in GLOW TDT file.
    
    The GEO file has explicit boundary condition groups:
      BC 1: [1, 5, 9, 25, 32, 36, 40]
      BC 2: [13, 17, 21, 56, 77, 81, 85]
      BC 3: [46, 49, 52, 67, 106, 109, 112]
      BC 4: [70, 73, 76, 91, 97, 100, 103]
    
    This function finds the corresponding element IDs in the GLOW file by matching
    element coordinates (cx, cy, dx, dy).
    
    Returns the mapped boundary condition groups for GLOW.
    """
    print("\n" + "=" * 80)
    print("MAPPING GEO BOUNDARY ELEMENTS TO GLOW")
    print("=" * 80)
    
    # Parse both files
    geo_parser = TDTDatParser(geo_tdt_path)
    geo_data = geo_parser.parse()
    
    glow_parser = TDTDatParser(glow_tdt_path)
    glow_data = glow_parser.parse()
    
    # GEO boundary condition groups (from the GEO file)
    geo_bc_groups = {
        1: [1, 5, 9, 25, 32, 36, 40],      # One side
        2: [13, 17, 21, 56, 77, 81, 85],   # Opposite side
        3: [46, 49, 52, 67, 106, 109, 112], # Third side
        4: [70, 73, 76, 91, 97, 100, 103],  # Fourth side
    }
    
    # Calculate coordinate offset between GEO and GLOW
    # GEO: origin at (0, 0)
    # GLOW: origin offset (need to determine from data)
    
    # Get sample coordinates to find offset
    geo_sample_coords = geo_data.element_coords.get(1, (0, 0, 0, 0))
    glow_sample_coords = None
    
    # Find a matching element by looking at relative geometry
    # The geometries are the same, just with different origins
    print("\nDetermining coordinate offset between GEO and GLOW...")
    
    # Get bounding boxes
    geo_cx = [c[0] for c in geo_data.element_coords.values() if c[0] is not None]
    geo_cy = [c[1] for c in geo_data.element_coords.values() if c[1] is not None]
    glow_cx = [c[0] for c in glow_data.element_coords.values() if c[0] is not None]
    glow_cy = [c[1] for c in glow_data.element_coords.values() if c[1] is not None]
    
    geo_min_x, geo_min_y = min(geo_cx), min(geo_cy)
    glow_min_x, glow_min_y = min(glow_cx), min(glow_cy)
    
    offset_x = glow_min_x - geo_min_x
    offset_y = glow_min_y - geo_min_y
    
    print(f"  GEO origin (min coords):  ({geo_min_x:.4f}, {geo_min_y:.4f})")
    print(f"  GLOW origin (min coords): ({glow_min_x:.4f}, {glow_min_y:.4f})")
    print(f"  Offset: ({offset_x:.4f}, {offset_y:.4f})")
    
    def find_matching_glow_element(geo_elem_id: int) -> Optional[int]:
        """Find the GLOW element that matches a GEO element by coordinates.
        
        Elements are line segments from (cx, cy) to (cx+dx, cy+dy).
        We match by finding elements that cover the same physical segment,
        regardless of direction (dx, dy may have opposite signs).
        """
        if geo_elem_id not in geo_data.element_coords:
            return None
        
        geo_cx, geo_cy, geo_dx, geo_dy = geo_data.element_coords[geo_elem_id]
        
        # Calculate the two endpoints of the GEO segment
        geo_start = (geo_cx, geo_cy)
        geo_end = (geo_cx + geo_dx, geo_cy + geo_dy)
        
        # Apply offset
        geo_start = (geo_start[0] + offset_x, geo_start[1] + offset_y)
        geo_end = (geo_end[0] + offset_x, geo_end[1] + offset_y)
        
        # Search for matching element in GLOW
        tolerance = 0.01  # Slightly larger tolerance
        
        for glow_elem_id, (glow_cx, glow_cy, glow_dx, glow_dy) in glow_data.element_coords.items():
            glow_start = (glow_cx, glow_cy)
            glow_end = (glow_cx + glow_dx, glow_cy + glow_dy)
            
            # Check if segments match (either same direction or reversed)
            same_direction = (
                abs(glow_start[0] - geo_start[0]) < tolerance and
                abs(glow_start[1] - geo_start[1]) < tolerance and
                abs(glow_end[0] - geo_end[0]) < tolerance and
                abs(glow_end[1] - geo_end[1]) < tolerance
            )
            
            reversed_direction = (
                abs(glow_start[0] - geo_end[0]) < tolerance and
                abs(glow_start[1] - geo_end[1]) < tolerance and
                abs(glow_end[0] - geo_start[0]) < tolerance and
                abs(glow_end[1] - geo_start[1]) < tolerance
            )
            
            if same_direction or reversed_direction:
                return glow_elem_id
        
        return None
    
    # Map each BC group
    glow_bc_groups = {}
    
    for bc_num, geo_elems in geo_bc_groups.items():
        print(f"\n--- Boundary Condition Group {bc_num} ---")
        print(f"  GEO elements: {geo_elems}")
        
        glow_elems = []
        for geo_elem in geo_elems:
            glow_elem = find_matching_glow_element(geo_elem)
            if glow_elem:
                glow_elems.append(glow_elem)
                # Show the mapping
                geo_coords = geo_data.element_coords.get(geo_elem, (None,)*4)
                glow_coords = glow_data.element_coords.get(glow_elem, (None,)*4)
                print(f"    GEO {geo_elem:3d} -> GLOW {glow_elem:3d}  "
                      f"(cx={geo_coords[0]:.3f}, cy={geo_coords[1]:.3f}) -> "
                      f"(cx={glow_coords[0]:.3f}, cy={glow_coords[1]:.3f})")
            else:
                print(f"    GEO {geo_elem:3d} -> GLOW ???  (no match found)")
        
        glow_bc_groups[bc_num] = sorted(glow_elems)
        print(f"  GLOW elements: {glow_bc_groups[bc_num]}")
    
    # Print summary for easy copy-paste into GLOW generator
    print("\n" + "=" * 80)
    print("GLOW BOUNDARY CONDITION GROUPS (for TDT file)")
    print("=" * 80)
    print("""
To fix the GLOW TDT file, add these boundary condition definitions:

* boundaries conditions: defaul nbbcda allsur
  0, 4, 0
""")
    
    for bc_num, elems in glow_bc_groups.items():
        elem_str = ", ".join(str(e) for e in elems)
        print(f"* BC group {bc_num}: nber = {len(elems)}")
        print(f"  elements: {elem_str}")
        print()
    
    # Also print in a format suitable for Python code
    print("\n--- Python dict format ---")
    print("glow_boundary_groups = {")
    for bc_num, elems in glow_bc_groups.items():
        print(f"    {bc_num}: {elems},")
    print("}")
    
    return glow_bc_groups


def main():
    """Main function to run tracking comparison."""
    # Define paths
    base_path = Path(__file__).parent
    salt_output_path = base_path / "SALT_tracking_output"
    glow_tdt_path = base_path.parent.parent / "tdt_data" / "AT10_BOX_TISO.dat"
    geo_tdt_path = base_path / "GEO_G2S_tdt_data" / "AT10_BOX_TISO_GEO.dat"
    
    # Parse GLOW TDT input file
    print("Parsing GLOW TDT input file...")
    tdt_parser = TDTDatParser(str(glow_tdt_path))
    tdt_data = tdt_parser.parse()
    
    # Parse SALT output files (GLOW versions with renamed files)
    moc_data = None
    cp_data = None
    ic_data = None
    
    # Try new file names first, then fall back to old names
    moc_file = salt_output_path / "glow_SALT_MOC_BOX.out"
    if not moc_file.exists():
        moc_file = salt_output_path / "SALT_MOC_BOX.out"
    
    cp_file = salt_output_path / "glow_SALT_CP_BOX.out"
    if not cp_file.exists():
        cp_file = salt_output_path / "SALT_CP_BOX.out"
    
    ic_file = salt_output_path / "glow_SALT_IC_BOX.out"
    if not ic_file.exists():
        ic_file = salt_output_path / "SALT_IC_BOX.out"
    
    if moc_file.exists():
        print("Parsing GLOW MOC tracking output...")
        moc_parser = SALTOutputParser(str(moc_file))
        moc_data = moc_parser.parse()
    
    if cp_file.exists():
        print("Parsing GLOW CP tracking output...")
        cp_parser = SALTOutputParser(str(cp_file))
        cp_data = cp_parser.parse()
    
    if ic_file.exists():
        print("Parsing GLOW IC (multicell) tracking output...")
        ic_parser = SALTOutputParser(str(ic_file))
        ic_data = ic_parser.parse()
    
    # Run comparison
    comparator = TrackingComparator(tdt_data, moc_data, cp_data, ic_data)
    results = comparator.print_report()
    
    # Detailed volume analysis
    if moc_data:
        analyze_volume_distribution(moc_data, tdt_data)
    if ic_data:
        analyze_volume_distribution(ic_data, tdt_data)
    
    # Additional IC-specific analysis
    if ic_data:
        print("\n" + "-" * 40)
        print("GLOW IC METHOD SPECIFIC ANALYSIS")
        print("-" * 40)
        print(f"  MACRO flux count: {ic_data.macro_flux_count}")
        print(f"  Perimeter elements: {len(ic_data.perimeter_elements)}")
        print(f"  IJAT (interface currents): {ic_data.ijat}")
        print(f"  NMIX (perimeter elements): {ic_data.nmix}")
        
        if ic_data.macro_flux_count != ic_data.nreg:
            print(f"\n  ⚠ POTENTIAL ISSUE:")
            print(f"    Macro flux count ({ic_data.macro_flux_count}) != NREG ({ic_data.nreg})")
            print(f"    This suggests the IC method treats one region differently")
    
    # GLOW vs GEO comparison
    glow_ic, geo_ic = compare_glow_vs_geo()
    
    # TDT file connectivity analysis
    if geo_tdt_path.exists():
        analyze_tdt_connectivity(glow_tdt_path, geo_tdt_path)
    
    # Boundary condition definition analysis (ROOT CAUSE)
    if geo_tdt_path.exists():
        analyze_boundary_condition_definitions(str(glow_tdt_path), str(geo_tdt_path))
    
    # Map GEO boundary elements to GLOW element IDs
    if geo_tdt_path.exists():
        glow_bc_groups = map_geo_to_glow_boundary_elements(str(geo_tdt_path), str(glow_tdt_path))
    
    # Print final conclusions
    print_final_conclusions()
    
    return results


def print_final_conclusions():
    """Print final conclusions after GLOW vs GEO comparison."""
    print("\n" + "=" * 80)
    print("FINAL CONCLUSIONS")
    print("=" * 80)
    
    print("""
================================================================================
                         ROOT CAUSE IDENTIFIED
================================================================================

The missing region in GLOW's IC tracking is caused by MISSING EXPLICIT BOUNDARY
CONDITION DEFINITIONS in the TDT file.

EVIDENCE:
---------
1. GEO-generated TDT file → SALT IC correctly tracks all 49 regions
2. GLOW-generated TDT file → SALT IC only tracks 48 regions (missing central)
3. Both files have 28 boundary elements correctly connected to node 0

KEY DIFFERENCE IN BOUNDARY CONDITION SECTION:
---------------------------------------------
GLOW TDT file:
  * boundaries conditions: defaul nbbcda allsur
    0, 0, 0
  
  → nbbcda = 0 means NO explicit boundary condition groups are defined
  → SALT must INFER which elements belong to which side
  → This inference fails and creates 8 ICODEs instead of 4

GEO TDT file:
  *defaul  nbbcda  allsur  divsur  ndivsur
       0     4     0     0     0
  
  → nbbcda = 4 means 4 explicit boundary condition groups are defined
  → Each group lists exactly which 7 elements belong to it:
      BC 1: [1, 5, 9, 25, 32, 36, 40]      (one side)
      BC 2: [13, 17, 21, 56, 77, 81, 85]   (opposite side)
      BC 3: [46, 49, 52, 67, 106, 109, 112] (third side)
      BC 4: [70, 73, 76, 91, 97, 100, 103]  (fourth side)
  → SALT uses these definitions → exactly 4 ICODEs

HOW THIS CAUSES THE MISSING REGION:
-----------------------------------
Without explicit BC definitions:
1. SALT IC infers boundary groups from element connectivity
2. The inference creates 8 boundary codes (possibly interpreting corners separately)
3. This creates 32 perimeter surfaces instead of 28
4. The macro geometry perimeter treatment incorrectly excludes the central region
5. Result: 48 flux regions instead of 49

FIX REQUIRED IN GLOW:
---------------------
GLOW's TDT generator (generator.py) needs to:
1. Set nbbcda = number_of_sides (typically 4 for rectangular geometries)
2. For each side, identify which boundary elements belong to it
3. Write explicit boundary condition groups listing the element IDs

Example fix for rectangular geometry:
  * boundaries conditions: defaul nbbcda allsur
    0, 4, 0
  
  * BC group 1: [left side element IDs]
  * BC group 2: [bottom side element IDs]
  * BC group 3: [right side element IDs]
  * BC group 4: [top side element IDs]

WORKAROUND:
-----------
Use MOC or CP tracking methods with GLOW-generated files - they work correctly.
Only the IC (multicell surfacic) method requires explicit BC definitions.
================================================================================
""")


