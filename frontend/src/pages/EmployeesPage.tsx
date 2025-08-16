import { Button } from '@/components/ui/button';
import { Badge } from '@/components/ui/badge';
import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/card';
import { Input } from '@/components/ui/input';
import { Select, SelectContent, SelectItem, SelectTrigger, SelectValue } from '@/components/ui/select';
import { Dialog, DialogContent, DialogDescription, DialogFooter, DialogHeader, DialogTitle, DialogTrigger } from '@/components/ui/dialog';
import { Label } from '@/components/ui/label';
import { Header } from '@/components/Header';
import { PageWrapper, PageSection } from '@/components/PageWrapper';
import { employees, type Employee } from '@/data/mockData';
import { generateId } from '@/lib/utils';
import { 
  ArrowLeft, 
  Search, 
  Filter, 
  Plus, 
  Users,
  MoreVertical,
  Building2,
  Mail,
  Phone,
  MapPin
} from 'lucide-react';
import { useState, type FC } from 'react';
import { Link } from 'react-router-dom';

const getDepartmentColor = (department: string) => {
  switch (department.toLowerCase()) {
    case 'engineering':
      return 'border-blue-600 bg-blue-50 text-blue-700 dark:border-blue-300 dark:bg-blue-100 dark:text-blue-800';
    case 'design':
      return 'border-purple-600 bg-purple-50 text-purple-700 dark:border-purple-300 dark:bg-purple-100 dark:text-purple-800';
    case 'product':
      return 'border-green-600 bg-green-50 text-green-700 dark:border-green-300 dark:bg-green-100 dark:text-green-800';
    case 'marketing':
      return 'border-orange-600 bg-orange-50 text-orange-700 dark:border-orange-300 dark:bg-orange-100 dark:text-orange-800';
    case 'sales':
      return 'border-red-600 bg-red-50 text-red-700 dark:border-red-300 dark:bg-red-100 dark:text-red-800';
    case 'hr':
      return 'border-pink-600 bg-pink-50 text-pink-700 dark:border-pink-300 dark:bg-pink-100 dark:text-pink-800';
    case 'executive':
      return 'border-gray-600 bg-gray-50 text-gray-700 dark:border-gray-300 dark:bg-gray-100 dark:text-gray-800';
    default:
      return 'border-muted-foreground/20 bg-muted text-muted-foreground';
  }
};

export const EmployeesPage: FC = () => {
  const [employeesList, setEmployeesList] = useState<Employee[]>(employees);
  const [searchQuery, setSearchQuery] = useState('');
  const [filterDepartment, setFilterDepartment] = useState('all');
  const [isAddDialogOpen, setIsAddDialogOpen] = useState(false);
  const [newEmployeeName, setNewEmployeeName] = useState('');
  const [newEmployeeRole, setNewEmployeeRole] = useState('');
  const [newEmployeeDepartment, setNewEmployeeDepartment] = useState<Employee['department']>('Engineering');
  const [newEmployeeEmail, setNewEmployeeEmail] = useState('');
  const [newEmployeePhone, setNewEmployeePhone] = useState('');
  const [newEmployeeLocation, setNewEmployeeLocation] = useState('');

  // Filter employees based on search query and department
  const filteredEmployees = employeesList.filter(employee => {
    const matchesSearch = employee.name.toLowerCase().includes(searchQuery.toLowerCase()) ||
                         employee.role.toLowerCase().includes(searchQuery.toLowerCase()) ||
                         employee.department.toLowerCase().includes(searchQuery.toLowerCase());
    const matchesDepartment = filterDepartment === 'all' || employee.department === filterDepartment;
    
    return matchesSearch && matchesDepartment;
  });

  const addEmployee = () => {
    if (!newEmployeeName.trim() || !newEmployeeRole.trim() || !newEmployeeEmail.trim()) return;

    const newEmployee: Employee = {
      id: generateId(),
      name: newEmployeeName.trim(),
      role: newEmployeeRole.trim(),
      department: newEmployeeDepartment,
      avatar: `https://api.dicebear.com/7.x/avataaars/svg?seed=${newEmployeeName.trim()}`,
      email: newEmployeeEmail.trim(),
      phone: newEmployeePhone.trim() || undefined,
      location: newEmployeeLocation.trim() || undefined
    };

    setEmployeesList(prev => [newEmployee, ...prev]);

    // Reset form
    setNewEmployeeName('');
    setNewEmployeeRole('');
    setNewEmployeeDepartment('Engineering');
    setNewEmployeeEmail('');
    setNewEmployeePhone('');
    setNewEmployeeLocation('');
    setIsAddDialogOpen(false);
  };

  const removeEmployee = (employeeId: string) => {
    setEmployeesList(prev => prev.filter(emp => emp.id !== employeeId));
  };

  return (
    <div className="min-h-screen bg-background">
      <Header />
      
      <PageWrapper className="mx-auto max-w-6xl px-4 sm:px-6 lg:px-8 py-6">
        {/* Header Section */}
        <PageSection index={0} className="mb-6">
          <div className="flex items-center gap-4 mb-4">
            <Link to="/">
              <Button variant="ghost" size="sm" className="gap-2">
                <ArrowLeft className="h-4 w-4" />
                Back to Dashboard
              </Button>
            </Link>
          </div>
          
          <div className="space-y-2">
            <h1 className="text-xl sm:text-2xl font-bold tracking-tight">Manage Employees</h1>
            <p className="text-sm sm:text-base text-muted-foreground">
              Manage your team, view employee details, and maintain organizational structure
            </p>
          </div>
        </PageSection>

        {/* Actions & Filters Section */}
        <PageSection index={1}>
          <Card className="mb-6">
          <CardHeader className="pb-3 sm:pb-4">
            <CardTitle className="text-base sm:text-lg">Employee Management</CardTitle>
          </CardHeader>
          <CardContent className="space-y-4 sm:space-y-6">
            {/* First Row - Search and Create */}
            <div className="flex flex-col gap-3 sm:flex-row sm:gap-4 sm:items-end">
              <div className="flex-1">
                <div className="relative">
                  <Search className="absolute left-3 top-1/2 transform -translate-y-1/2 h-4 w-4 text-muted-foreground" />
                  <Input
                    placeholder="Search employees..."
                    value={searchQuery}
                    onChange={(e) => setSearchQuery(e.target.value)}
                    className="pl-10"
                  />
                </div>
              </div>
              
              {/* Create Employee Button */}
              <Dialog open={isAddDialogOpen} onOpenChange={setIsAddDialogOpen}>
                <DialogTrigger asChild>
                  <Button className="gap-2 w-full sm:w-auto whitespace-nowrap">
                    <Plus className="h-4 w-4" />
                    <span className="sm:hidden">Add Employee</span>
                    <span className="hidden sm:inline">New Employee</span>
                  </Button>
                </DialogTrigger>
                  <DialogContent className="sm:max-w-[500px] mx-4">
                    <DialogHeader>
                      <DialogTitle>Add New Employee</DialogTitle>
                      <DialogDescription>
                        Add a new team member to your organization.
                      </DialogDescription>
                    </DialogHeader>
                    <div className="grid gap-4 py-4">
                      <div className="grid grid-cols-1 sm:grid-cols-4 items-center gap-4">
                        <Label htmlFor="name" className="sm:text-right">
                          Name
                        </Label>
                        <Input
                          id="name"
                          value={newEmployeeName}
                          onChange={(e) => setNewEmployeeName(e.target.value)}
                          placeholder="Enter employee name"
                          className="sm:col-span-3"
                        />
                      </div>
                      <div className="grid grid-cols-1 sm:grid-cols-4 items-center gap-4">
                        <Label htmlFor="role" className="sm:text-right">
                          Role
                        </Label>
                        <Input
                          id="role"
                          value={newEmployeeRole}
                          onChange={(e) => setNewEmployeeRole(e.target.value)}
                          placeholder="Enter job role"
                          className="sm:col-span-3"
                        />
                      </div>
                      <div className="grid grid-cols-1 sm:grid-cols-4 items-center gap-4">
                        <Label htmlFor="department" className="sm:text-right">
                          Department
                        </Label>
                        <Select value={newEmployeeDepartment} onValueChange={(value: Employee['department']) => setNewEmployeeDepartment(value)}>
                          <SelectTrigger className="sm:col-span-3">
                            <SelectValue />
                          </SelectTrigger>
                          <SelectContent>
                            <SelectItem value="Engineering">Engineering</SelectItem>
                            <SelectItem value="Design">Design</SelectItem>
                            <SelectItem value="Product">Product</SelectItem>
                            <SelectItem value="Marketing">Marketing</SelectItem>
                            <SelectItem value="Sales">Sales</SelectItem>
                            <SelectItem value="HR">HR</SelectItem>
                            <SelectItem value="Executive">Executive</SelectItem>
                          </SelectContent>
                        </Select>
                      </div>
                      <div className="grid grid-cols-1 sm:grid-cols-4 items-center gap-4">
                        <Label htmlFor="email" className="sm:text-right">
                          Email
                        </Label>
                        <Input
                          id="email"
                          type="email"
                          value={newEmployeeEmail}
                          onChange={(e) => setNewEmployeeEmail(e.target.value)}
                          placeholder="Enter email address"
                          className="sm:col-span-3"
                        />
                      </div>
                      <div className="grid grid-cols-1 sm:grid-cols-4 items-center gap-4">
                        <Label htmlFor="phone" className="sm:text-right">
                          Phone
                        </Label>
                        <Input
                          id="phone"
                          value={newEmployeePhone}
                          onChange={(e) => setNewEmployeePhone(e.target.value)}
                          placeholder="Enter phone number (optional)"
                          className="sm:col-span-3"
                        />
                      </div>
                      <div className="grid grid-cols-1 sm:grid-cols-4 items-center gap-4">
                        <Label htmlFor="location" className="sm:text-right">
                          Location
                        </Label>
                        <Input
                          id="location"
                          value={newEmployeeLocation}
                          onChange={(e) => setNewEmployeeLocation(e.target.value)}
                          placeholder="Enter location (optional)"
                          className="sm:col-span-3"
                        />
                      </div>
                    </div>
                    <DialogFooter>
                      <Button 
                        onClick={addEmployee}
                        disabled={!newEmployeeName.trim() || !newEmployeeRole.trim() || !newEmployeeEmail.trim()}
                      >
                        Add Employee
                      </Button>
                    </DialogFooter>
                  </DialogContent>
                </Dialog>
              </div>

              {/* Second Row - Filters */}
              <div className="flex flex-col gap-3 sm:flex-row sm:gap-4 sm:items-center">
                {/* Department Filter */}
                <div className="w-full sm:w-56">
                  <Select value={filterDepartment} onValueChange={setFilterDepartment}>
                    <SelectTrigger className="gap-2 h-10 w-full">
                      <Filter className="h-4 w-4" />
                      <SelectValue placeholder="Filter by department" />
                    </SelectTrigger>
                    <SelectContent>
                      <SelectItem value="all">All Departments</SelectItem>
                      <SelectItem value="Engineering">Engineering</SelectItem>
                      <SelectItem value="Design">Design</SelectItem>
                      <SelectItem value="Product">Product</SelectItem>
                      <SelectItem value="Marketing">Marketing</SelectItem>
                      <SelectItem value="Sales">Sales</SelectItem>
                      <SelectItem value="HR">HR</SelectItem>
                      <SelectItem value="Executive">Executive</SelectItem>
                    </SelectContent>
                  </Select>
                </div>
                
                {/* Spacer for alignment */}
                <div className="flex-1 hidden sm:block" />
              </div>
              
              {/* Results Count */}
              <div className="text-xs sm:text-sm text-muted-foreground">
                Showing {filteredEmployees.length} of {employeesList.length} employees
              </div>
          </CardContent>
        </Card>
        </PageSection>

        {/* Employees Grid */}
        {filteredEmployees.length === 0 ? (
          <PageSection index={2}>
            <Card>
              <CardContent className="flex flex-col items-center justify-center py-8 sm:py-12">
                <div className="text-center space-y-3 max-w-sm mx-auto px-4">
                  <div className="h-10 w-10 sm:h-12 sm:w-12 mx-auto bg-muted rounded-full flex items-center justify-center">
                    <Users className="h-5 w-5 sm:h-6 sm:w-6 text-muted-foreground" />
                  </div>
                  <h3 className="font-medium text-sm sm:text-base">
                    {searchQuery ? 'No employees found' : 'No employees yet'}
                  </h3>
                  <p className="text-xs sm:text-sm text-muted-foreground">
                    {searchQuery 
                      ? 'Try adjusting your search or filter criteria'
                      : 'Add your first employee to get started'
                    }
                  </p>
                  {!searchQuery && (
                    <Dialog open={isAddDialogOpen} onOpenChange={setIsAddDialogOpen}>
                      <DialogTrigger asChild>
                        <Button className="mt-3 sm:mt-4 gap-2 w-full sm:w-auto">
                          <Plus className="h-4 w-4" />
                          Add First Employee
                        </Button>
                      </DialogTrigger>
                    </Dialog>
                  )}
              </div>
            </CardContent>
          </Card>
        </PageSection>
        ) : (
          <PageSection index={2}>
            <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-4">
              {filteredEmployees.map((employee, index) => (
                <Card key={employee.id} className="hover:shadow-md transition-shadow">
                  <CardContent className="p-4 sm:p-6">
                    <div className="flex items-start gap-3 sm:gap-4">
                      <div className="flex-shrink-0">
                        <img 
                          src={employee.avatar} 
                          alt={employee.name}
                          className="h-12 w-12 rounded-full border-2 border-gray-200"
                        />
                      </div>
                      
                      <div className="flex-1 space-y-3 sm:space-y-4 min-w-0">
                        {/* Employee Header */}
                        <div className="flex items-start justify-between gap-2">
                          <div className="space-y-2 flex-1 min-w-0">
                            <div className="flex flex-col sm:flex-row sm:items-center gap-2 sm:gap-3">
                              <h3 className="font-semibold text-base sm:text-lg truncate">{employee.name}</h3>
                              <div className="flex flex-wrap gap-2">
                                <Badge 
                                  variant="outline"
                                  className={`text-xs ${getDepartmentColor(employee.department)}`}
                                >
                                  {employee.department}
                                </Badge>
                                <Badge 
                                  variant="outline"
                                  className="text-xs border-blue-200 bg-blue-50 text-blue-700"
                                >
                                  {employee.role}
                                </Badge>
                              </div>
                            </div>
                          </div>
                          
                          <div className="flex items-center gap-2">
                            <Button variant="ghost" size="sm" className="flex-shrink-0">
                              <MoreVertical className="h-4 w-4" />
                            </Button>
                            <Button 
                              variant="outline" 
                              size="sm" 
                              className="flex-shrink-0 text-red-600 hover:text-red-700 hover:bg-red-50"
                              onClick={() => removeEmployee(employee.id)}
                            >
                              Remove
                            </Button>
                          </div>
                        </div>

                        {/* Employee Contact Info */}
                        <div className="grid grid-cols-1 sm:grid-cols-2 gap-3 text-sm">
                          {employee.email && (
                            <div className="flex items-center gap-2 text-muted-foreground">
                              <Mail className="h-4 w-4 flex-shrink-0" />
                              <span className="truncate">{employee.email}</span>
                            </div>
                          )}
                          {employee.phone && (
                            <div className="flex items-center gap-2 text-muted-foreground">
                              <Phone className="h-4 w-4 flex-shrink-0" />
                              <span className="truncate">{employee.phone}</span>
                            </div>
                          )}
                          {employee.location && (
                            <div className="flex items-center gap-2 text-muted-foreground">
                              <MapPin className="h-4 w-4 flex-shrink-0" />
                              <span className="truncate">{employee.location}</span>
                            </div>
                          )}
                        </div>

                        {/* Employee Meta Info */}
                        <div className="flex flex-wrap items-center gap-2 sm:gap-4 text-xs text-muted-foreground">
                          <div className="flex items-center gap-1">
                            <Building2 className="h-3 w-3 flex-shrink-0" />
                            <span className="truncate">Dept: {employee.department}</span>
                          </div>
                          <div className="flex items-center gap-1">
                            <Users className="h-3 w-3 flex-shrink-0" />
                            <span>Role: {employee.role}</span>
                          </div>
                        </div>
                      </div>
                    </div>
                  </CardContent>
                </Card>
              ))}
            </div>
          </PageSection>
        )}

        {/* Load More Button (for future pagination) */}
        {filteredEmployees.length > 0 && (
          <div className="mt-6 sm:mt-8 text-center px-4">
            <Button variant="outline" disabled className="w-full sm:w-auto">
              Load More Employees
            </Button>
            <p className="text-xs text-muted-foreground mt-2">
              All employees loaded
            </p>
          </div>
        )}
      </PageWrapper>
    </div>
  );
};
